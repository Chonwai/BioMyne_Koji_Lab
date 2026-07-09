#!/usr/bin/env python3
"""Discover candidate article URLs for a source via Firecrawl /v2/map.

This helper keeps the shell pipeline small and makes source-specific URL
discovery testable in isolation.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from functools import lru_cache
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

import yaml

try:
    from _pipeline_normalization import normalize_url
except ModuleNotFoundError:
    from ops.scripts._pipeline_normalization import normalize_url


ARTICLE_KEYWORDS = (
    "/article/",
    "/articles/",
    "/news/",
    "/story/",
    "/stories/",
    "/post/",
    "/posts/",
    "/read/",
    "/abs/",
)

NON_ARTICLE_PATTERNS = (
    r"/about(?:/|$)",
    r"/author(?:/|$)",
    r"/authors(?:/|$)",
    r"/staff(?:/|$)",
    r"/tag(?:/|$)",
    r"/category(?:/|$)",
    r"/categories(?:/|$)",
    r"/topics?(?:/|$)",
    r"/events?(?:/|$)",
    r"/jobs?(?:/|$)",
    r"/careers?(?:/|$)",
    r"/contact(?:/|$)",
    r"/privacy(?:/|$)",
    r"/terms(?:/|$)",
    r"/newsletter(?:/|$)",
    r"/subscribe(?:/|$)",
    r"/login(?:/|$)",
    r"/search(?:/|$)",
    r"/sitemap",
    r"/wp-json",
    r"/content/early/",
    r"\.xml$",
)

DATE_PATTERNS = (
    re.compile(r"/20\d{2}/\d{2}/\d{2}/"),
    re.compile(r"/20\d{2}/\d{2}/"),
)

DATE_CAPTURE = re.compile(r"/(20\d{2})/(\d{2})(?:/(\d{2}))?/")
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent


@dataclass(frozen=True)
class SourceRule:
    discovery_url: Optional[str] = None
    map_search: Optional[str] = None
    sitemap: str = "include"
    include_keywords: Sequence[str] = ()
    include_regexes: Sequence[str] = ()
    exclude_regexes: Sequence[str] = ()
    non_article_exceptions: Sequence[str] = ()
    disable_category_stop_on_last_seen: bool = False
    coarse_feed_timestamps: bool = False


SOURCE_RULES: Dict[str, SourceRule] = {
    "STAT News": SourceRule(
        include_regexes=(r"/20\d{2}/\d{2}/\d{2}/", r"/pharmalot/20\d{2}/\d{2}/\d{2}/"),
    ),
    "BioPharma Dive": SourceRule(
        include_regexes=(r"/news/.+?/\d+/",),
    ),
    "Nature Biotechnology": SourceRule(
        include_keywords=("/articles/",),
        include_regexes=(r"/articles/s\d{5}-\d{3}-\d{5}-[\w-]+$",),
    ),
    "Fierce Biotech": SourceRule(
        include_keywords=("/biotech/", "/research/"),
    ),
    "GEN – Genetic Engineering & Biotechnology News": SourceRule(
        include_keywords=("/news/",),
        include_regexes=(r"/topics/[^/]+/.+",),
        exclude_regexes=(r"/topics/[^/]+/$",),
        non_article_exceptions=(r"/topics/[^/]+/.+",),
    ),
    "Endpoints News": SourceRule(
        include_keywords=("/202", "/news/", "/biotech/", "/pharma/"),
        include_regexes=(r"^https?://(?:www\.)?endpoints\.news/(?:sp/)?[a-z0-9][^?#]+$",),
        exclude_regexes=(
            r"endpoints\.news/(?:news|rss|feed|channel|about|events?|author|tag|category)(?:/|$)",
            r"endpoints\.news/topic-hub/",
            r"endpoints\.news/.+/page/\d+(?:/|$)",
        ),
    ),
    "BioCentury": SourceRule(
        include_keywords=("/article/", "/biopharma/", "/business/"),
    ),
    "SynBioBeta": SourceRule(
        include_keywords=("/read/", "/article/"),
        exclude_regexes=(r"^https?://(?:www\.)?synbiobeta\.com/?$",),
    ),
    "arXiv Quantitative Biology": SourceRule(
        discovery_url="https://arxiv.org/list/q-bio/new",
        map_search="abs",
        sitemap="skip",
        include_keywords=("/abs/",),
        exclude_regexes=(r"/archive/", r"/list/"),
        coarse_feed_timestamps=True,
    ),
    "bioRxiv": SourceRule(
        discovery_url="https://www.biorxiv.org/content/early/recent",
        map_search="content/10.",
        sitemap="skip",
        include_regexes=(r"/content/10\.\d{4,9}/",),
        disable_category_stop_on_last_seen=True,
    ),
    "Science": SourceRule(
        discovery_url="https://www.science.org/toc/science/current",
        map_search="doi",
        sitemap="skip",
        include_keywords=("/doi/",),
    ),
}


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[dict] = []
        self._current_href: Optional[str] = None
        self._current_text: List[str] = []
        self._current_rel: str = ""

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        if len(self.links) >= category_target_max_links_per_page():
            return
        if tag.lower() != "a":
            return
        attr_map = dict(attrs)
        self._current_href = attr_map.get("href")
        self._current_rel = attr_map.get("rel") or ""
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current_href is None:
            return
        self.links.append(
            {
                "href": self._current_href,
                "text": "".join(self._current_text).strip(),
                "rel": self._current_rel,
            }
        )
        self._current_href = None
        self._current_text = []
        self._current_rel = ""


RETRYABLE_HTTP_CODES = {408, 409, 425, 429, 500, 502, 503, 504}


def fetch_url_bytes(url: str, timeout_seconds: int = 30) -> bytes:
    attempts = env_int("DISCOVERY_HTTP_RETRY_ATTEMPTS", 4)
    timeout_budget = env_int("DISCOVERY_HTTP_TIMEOUT_SECONDS", timeout_seconds)
    last_error: Exception | None = None

    for attempt in range(attempts):
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "BioMyne-Koji/1.0 (+https://www.biomyne.com)",
                "Connection": "close",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_budget) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in RETRYABLE_HTTP_CODES or attempt == attempts - 1:
                raise
        except Exception as exc:
            last_error = exc
            if attempt == attempts - 1:
                raise
        time.sleep(2 ** attempt)

    raise RuntimeError(f"HTTP fetch failed: {last_error}")


def firecrawl_map(url: str, search: Optional[str], sitemap: str, limit: int) -> List[dict]:
    token = os.environ.get("FIRECRAWL_KEY") or os.environ.get("FIRECRAWL_API_KEY")
    if not token:
        raise RuntimeError("FIRECRAWL_KEY or FIRECRAWL_API_KEY is required")

    timeout_ms = env_int("DISCOVERY_MAP_TIMEOUT_MS", 90000)
    retry_attempts = env_int("DISCOVERY_MAP_RETRY_ATTEMPTS", 5)
    payload = {
        "url": url,
        "sitemap": sitemap,
        "includeSubdomains": False,
        "ignoreQueryParameters": True,
        "limit": limit,
        "timeout": timeout_ms,
    }
    if search:
        payload["search"] = search

    last_error = None
    for attempt in range(retry_attempts):
        req = urllib.request.Request(
            "https://api.firecrawl.dev/v2/map",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=max(70, (timeout_ms // 1000) + 20)) as resp:
                data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in RETRYABLE_HTTP_CODES or attempt == retry_attempts - 1:
                raise
            time.sleep(2 ** attempt)
        except Exception as exc:
            last_error = exc
            if attempt == retry_attempts - 1:
                raise
            time.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"Firecrawl map failed: {last_error}")

    links = data.get("links", [])
    if not isinstance(links, list):
        return []
    return [item for item in links if isinstance(item, dict) and item.get("url")]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_datetime(value: str) -> Optional[datetime]:
    raw = (value or "").strip()
    if not raw:
        return None

    try:
        if raw.endswith("Z"):
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return datetime.fromisoformat(raw)
    except ValueError:
        pass

    try:
        return parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None


def iso_datetime(value: str) -> Optional[str]:
    parsed = parse_datetime(value)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if parsed else None


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def child_text(element: ET.Element, names: Sequence[str]) -> str:
    wanted = {name.lower() for name in names}
    for child in element:
        if local_name(child.tag).lower() in wanted:
            return (child.text or "").strip()
    return ""


def child_link(element: ET.Element) -> str:
    for child in element:
        tag = local_name(child.tag).lower()
        if tag != "link":
            continue
        href = child.attrib.get("href")
        rel = child.attrib.get("rel", "alternate")
        if href and rel in ("alternate", ""):
            return href.strip()
        if child.text and child.text.strip():
            return child.text.strip()
    return ""


def supabase_headers() -> Optional[dict]:
    supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    if not supabase_key:
        return None
    return {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }


def supabase_request(method: str, path: str, body: Optional[dict] = None) -> tuple[int, object]:
    supabase_url = os.environ.get("SUPABASE_URL", "")
    headers = supabase_headers()
    if not supabase_url or not headers:
        return 0, {"error": "supabase_not_configured"}

    data_bytes = None
    request_headers = dict(headers)
    if body is not None:
        request_headers["Prefer"] = "return=representation"
        data_bytes = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        f"{supabase_url}{path}",
        data=data_bytes,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read().decode("utf-8")
            return resp.status, json.loads(payload) if payload.strip() else None
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore") if exc.fp else exc.reason
        return exc.code, {"error": body_text}
    except Exception as exc:
        return 0, {"error": str(exc)}


@lru_cache(maxsize=1)
def load_manifest_sources() -> Dict[str, dict]:
    manifest_path = os.environ.get("SOURCE_MANIFEST_PATH", "ops/source-manifests/biotech.yaml")
    path = Path(manifest_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.exists():
        return {}

    data = yaml.safe_load(path.read_text()) or {}
    sources = data.get("sources", []) if isinstance(data, dict) else []
    result: Dict[str, dict] = {}
    for item in sources:
        if isinstance(item, dict) and item.get("name"):
            result[item["name"]] = item
    return result


def manifest_source_settings(source_name: str) -> dict:
    return load_manifest_sources().get(source_name, {})


def read_source_state() -> dict:
    source_id = os.environ.get("SRC_ID", "").strip()
    if not source_id:
        return {}
    status, payload = supabase_request(
        "GET",
        f"/rest/v1/source_discovery_state?source_id=eq.{urllib.parse.quote(source_id, safe='')}&select=*",
    )
    if status == 200 and isinstance(payload, list) and payload:
        return payload[0]
    if status not in (0, 200):
        print(f"[discover] Failed to read source_discovery_state for {source_id}: {payload}", file=sys.stderr)
    return {}


def write_source_state(patch: dict) -> None:
    source_id = os.environ.get("SRC_ID", "").strip()
    if not source_id:
        return

    body = {"source_id": source_id, **patch, "updated_at": now_iso()}
    status, payload = supabase_request(
        "GET",
        f"/rest/v1/source_discovery_state?source_id=eq.{urllib.parse.quote(source_id, safe='')}&select=source_id",
    )

    if status == 200 and isinstance(payload, list) and payload:
        write_status, write_payload = supabase_request(
            "PATCH",
            f"/rest/v1/source_discovery_state?source_id=eq.{urllib.parse.quote(source_id, safe='')}",
            body,
        )
        if write_status not in (200, 204):
            print(f"[discover] Failed to update source_discovery_state for {source_id}: {write_payload}", file=sys.stderr)
    else:
        body.setdefault("created_at", now_iso())
        write_status, write_payload = supabase_request("POST", "/rest/v1/source_discovery_state", body)
        if write_status not in (200, 201):
            print(f"[discover] Failed to insert source_discovery_state for {source_id}: {write_payload}", file=sys.stderr)


def source_in_cooldown(state: dict, surface: str) -> bool:
    if state.get("cursor_type") != surface:
        return False
    cooldown_until = parse_datetime(str(state.get("cooldown_until") or ""))
    return bool(cooldown_until and cooldown_until > datetime.now(timezone.utc))


def cooldown_until_iso() -> str:
    hours = env_int("DISCOVERY_SURFACE_COOLDOWN_HOURS", 6)
    target = datetime.now(timezone.utc).timestamp() + (hours * 3600)
    return datetime.fromtimestamp(target, timezone.utc).isoformat().replace("+00:00", "Z")


def mark_surface_failure(surface: str, error: Exception | str) -> None:
    state = read_source_state()
    current_errors = int(state.get("error_count") or 0)
    patch = {
        "cursor_type": surface,
        "last_discovery_at": now_iso(),
        "last_error": str(error),
        "error_count": current_errors + 1,
    }
    if current_errors + 1 >= 3:
        patch["cooldown_until"] = cooldown_until_iso()
    write_source_state(patch)


def mark_surface_success(surface: str, payload: dict) -> None:
    patch = {
        "cursor_type": surface,
        "last_discovery_at": now_iso(),
        "last_successful_discovery_at": now_iso(),
        "error_count": 0,
        "last_error": None,
        "cooldown_until": None,
    }
    patch.update(payload)
    write_source_state(patch)


def load_xml_sitemap(url: str) -> List[dict]:
    body = fetch_url_bytes(url, timeout_seconds=30)

    root = ET.fromstring(body)
    namespace_match = re.match(r"\{(.+)\}", root.tag)
    namespace = namespace_match.group(1) if namespace_match else ""
    loc_tag = f"{{{namespace}}}loc" if namespace else "loc"

    links: List[dict] = []
    if local_name(root.tag).lower() == "sitemapindex":
        for sitemap in root:
            if local_name(sitemap.tag).lower() != "sitemap":
                continue
            loc = child_text(sitemap, ["loc"])
            if not loc:
                continue
            links.append(
                {
                    "url": loc,
                    "title": "",
                    "description": "",
                    "published_at": iso_datetime(child_text(sitemap, ["lastmod"])),
                    "is_sitemap": True,
                    "discovery_method": "sitemap",
                }
            )
        return links

    for url_entry in root:
        if local_name(url_entry.tag).lower() != "url":
            continue
        loc = child_text(url_entry, ["loc"])
        if not loc:
            continue
        links.append(
            {
                "url": loc,
                "title": "",
                "description": "",
                "published_at": iso_datetime(child_text(url_entry, ["lastmod"])),
                "discovery_method": "sitemap",
            }
        )
    return links


def fetch_feed_entries(feed_url: str) -> List[dict]:
    body = fetch_url_bytes(feed_url, timeout_seconds=30)

    root = ET.fromstring(body)
    entries: List[dict] = []

    if local_name(root.tag).lower() == "rss":
        channel = next((child for child in root if local_name(child.tag).lower() == "channel"), None)
        if channel is None:
            return entries
        for item in channel:
            if local_name(item.tag).lower() != "item":
                continue
            url = child_text(item, ["link"])
            if not url:
                continue
            entries.append(
                {
                    "url": url,
                    "title": child_text(item, ["title"]),
                    "description": child_text(item, ["description", "summary"]),
                    "published_at": iso_datetime(child_text(item, ["pubDate", "updated", "date"])),
                    "discovery_method": "rss",
                }
            )
        return entries

    if local_name(root.tag).lower() == "feed":
        for entry in root:
            if local_name(entry.tag).lower() != "entry":
                continue
            url = child_link(entry)
            if not url:
                continue
            entries.append(
                {
                    "url": url,
                    "title": child_text(entry, ["title"]),
                    "description": child_text(entry, ["summary", "content"]),
                    "published_at": iso_datetime(child_text(entry, ["updated", "published"])),
                    "discovery_method": "rss",
                }
            )

    if local_name(root.tag).lower() == "rdf":
        for item in root:
            if local_name(item.tag).lower() != "item":
                continue
            url = child_text(item, ["link"])
            if not url:
                continue
            entries.append(
                {
                    "url": url,
                    "title": child_text(item, ["title"]),
                    "description": child_text(item, ["description", "encoded"]),
                    "published_at": iso_datetime(child_text(item, ["pubDate", "updated", "date"])),
                    "discovery_method": "rss",
                }
            )

    return entries


def feed_candidates(feed_url: str, limit: int, state: dict, rule: SourceRule, extraction_mode: str) -> List[dict]:
    entries = fetch_feed_entries(feed_url)
    last_cursor = parse_datetime(str(state.get("last_cursor_published_at") or ""))
    last_cursor_url = normalize_url(str(state.get("last_cursor_url") or "").strip()) if state.get("last_cursor_url") else ""
    candidates = []
    for item in entries:
        url = item.get("url", "").strip()
        if not url:
            continue
        published_at = parse_datetime(str(item.get("published_at") or ""))
        normalized_url = normalize_url(url)
        if last_cursor and published_at:
            if published_at < last_cursor:
                continue
            if published_at == last_cursor:
                if not rule.coarse_feed_timestamps:
                    continue
                if last_cursor_url and normalized_url == last_cursor_url:
                    continue
        score = score_link(url, item.get("title", ""), item.get("description", ""), rule, extraction_mode) + 4
        if score < candidate_score_threshold():
            continue
        candidates.append({**item, "score": score})

    candidates.sort(
        key=lambda item: (
            -score_link(item.get("url", ""), item.get("title", ""), item.get("description", ""), rule, extraction_mode),
            item.get("published_at") or "",
            item.get("url", ""),
        ),
        reverse=True,
    )
    return candidates[:limit]


def sitemap_candidates(source_name: str, limit: int, state: dict, rule: SourceRule, extraction_mode: str) -> List[dict]:
    sitemap_urls = manifest_source_settings(source_name).get("sitemap_urls", [])
    if not sitemap_urls and source_name == "Nature Biotechnology":
        sitemap_urls = recent_nature_article_sitemaps()

    raw_links: List[dict] = []
    for sitemap_url in sitemap_urls:
        try:
            loaded = load_xml_sitemap(sitemap_url)
        except Exception as exc:
            print(
                f"[discover] Supplemental sitemap load failed for {source_name}: {sitemap_url} ({exc})",
                file=sys.stderr,
            )
            continue

        for item in loaded:
            if item.get("is_sitemap"):
                try:
                    raw_links.extend(load_xml_sitemap(item["url"]))
                except Exception as exc:
                    print(
                        f"[discover] Nested sitemap load failed for {source_name}: {item['url']} ({exc})",
                        file=sys.stderr,
                    )
                    continue
            else:
                raw_links.append(item)

    checkpoint = state.get("last_sitemap_checkpoint") or {}
    candidates = []
    for item in raw_links:
        url = item.get("url", "").strip()
        if not url:
            continue
        published_at = item.get("published_at")
        if published_at and isinstance(checkpoint, dict):
            max_checkpoint = max((value for value in checkpoint.values() if isinstance(value, str)), default="")
            if max_checkpoint and published_at <= max_checkpoint:
                continue
        score = score_link(url, item.get("title", ""), item.get("description", ""), rule, extraction_mode)
        if score < candidate_score_threshold():
            continue
        candidates.append({**item, "score": score, "discovery_method": "sitemap"})

    candidates.sort(key=lambda item: (-item["score"], item.get("published_at") or "", item.get("url", "")), reverse=True)
    return candidates[:limit]


def env_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return max(default, minimum)
    try:
        value = int(raw)
    except ValueError:
        print(
            f"[discover] Invalid integer for {name}={raw!r}; falling back to {default}",
            file=sys.stderr,
        )
        value = default
    return max(value, minimum)


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def recent_nature_article_sitemaps() -> List[str]:
    months_back = env_int("NATURE_SUPPLEMENTAL_SITEMAP_MONTHS", 4)

    current = date.today().replace(day=1)
    urls: List[str] = []
    for offset in range(months_back):
        year = current.year
        month = current.month - offset
        while month <= 0:
            month += 12
            year -= 1
        urls.append(f"https://www.nature.com/nbt/sitemap/{year}/{month:02d}/articles.xml")
    return urls


def configured_map_limit(limit: int) -> int:
    multiplier = env_int("DISCOVERY_MAP_LIMIT_MULTIPLIER", 20)
    minimum = env_int("DISCOVERY_MAP_MIN_LIMIT", 80)
    return max(limit * multiplier, minimum)


def candidate_score_threshold() -> int:
    return env_int("DISCOVERY_MIN_CANDIDATE_SCORE", 4)


def date_score_bonus() -> int:
    return env_int("DISCOVERY_DATE_SCORE_BONUS", 4)


def rss_strict_bonus() -> int:
    return env_int("DISCOVERY_RSS_STRICT_BONUS", 6)


def normalize_host(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def fetch_html(url: str) -> str:
    return fetch_url_bytes(url, timeout_seconds=30).decode("utf-8", errors="ignore")


def infer_published_at_from_url(url: str) -> Optional[str]:
    match = DATE_CAPTURE.search(url)
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3) or "1")
    return datetime(year, month, day, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def category_target_priority(priority: str) -> int:
    return {"high": 3, "medium": 2, "low": 1}.get((priority or "medium").lower(), 2)


def read_category_targets() -> List[dict]:
    source_id = os.environ.get("SRC_ID", "").strip()
    if not source_id:
        return []
    status, payload = supabase_request(
        "GET",
        f"/rest/v1/source_category_targets?source_id=eq.{urllib.parse.quote(source_id, safe='')}&enabled=eq.true&select=id,name,url,priority,check_frequency_hours,last_seen_url,last_checked_at,last_error,error_type",
    )
    if status == 200 and isinstance(payload, list):
        return sorted(
            payload,
            key=lambda item: (
                -category_target_priority(str(item.get("priority") or "medium")),
                str(item.get("name") or ""),
            ),
        )
    return []


def update_category_target(target_id: str, patch: dict) -> None:
    if not target_id:
        return
    body = {**patch, "updated_at": now_iso()}
    supabase_request(
        "PATCH",
        f"/rest/v1/source_category_targets?id=eq.{urllib.parse.quote(target_id, safe='')}",
        body,
    )


def target_due(target: dict) -> bool:
    check_frequency_hours = int(target.get("check_frequency_hours") or 24)
    last_checked_at = parse_datetime(str(target.get("last_checked_at") or ""))
    if not last_checked_at:
        return True
    if last_checked_at.tzinfo is None:
        last_checked_at = last_checked_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last_checked_at >= timedelta(hours=check_frequency_hours)


def category_target_max_pages() -> int:
    return env_int("CATEGORY_TARGET_MAX_PAGES", 3)


def category_target_min_limit() -> int:
    return env_int("CATEGORY_TARGET_MIN_LIMIT", 10)


def category_target_max_links_per_page() -> int:
    return env_int("CATEGORY_TARGET_MAX_LINKS_PER_PAGE", 250)


def same_domain(candidate_url: str, source_url: str) -> bool:
    candidate_host = normalize_host(candidate_url)
    source_host = normalize_host(source_url)
    return candidate_host == source_host or candidate_host.endswith(f".{source_host}")


def extract_category_page_links(page_url: str, html: str) -> tuple[List[dict], Optional[str]]:
    parser = AnchorParser()
    parser.feed(html)
    next_url = None
    for link in parser.links:
        href = (link.get("href") or "").strip()
        if not href:
            continue
        rel = str(link.get("rel") or "").lower()
        text = str(link.get("text") or "").strip().lower()
        if next_url is None and (
            "next" in rel or text in {"next", "next page", ">", ">>", "›", "→", "older", "older posts"} or text.startswith("next")
        ):
            next_url = normalize_url(urllib.parse.urljoin(page_url, href))
    return parser.links, next_url


def category_page_candidates(
    source_name: str,
    source_url: str,
    limit: int,
    rule: SourceRule,
    extraction_mode: str,
    targets: List[dict],
    force_targets: bool = False,
) -> Optional[List[dict]]:
    if not targets:
        return None

    per_target_limit = max(category_target_min_limit(), limit * 3)
    collected: List[dict] = []
    attempted_targets = 0
    failed_targets = 0

    for target in targets:
        if not force_targets and not target_due(target):
            continue
        attempted_targets += 1

        target_id = str(target.get("id") or "")
        current_url = str(target.get("url") or "").strip()
        if not current_url:
            continue

        last_seen_url = normalize_url(str(target.get("last_seen_url") or "").strip()) if target.get("last_seen_url") else ""
        stop_on_last_seen = not rule.disable_category_stop_on_last_seen
        target_candidates: List[dict] = []
        newest_url = None

        try:
            for _ in range(category_target_max_pages()):
                html = fetch_html(current_url)
                links, next_url = extract_category_page_links(current_url, html)
                stop_reached = False

                for link in links:
                    href = (link.get("href") or "").strip()
                    if not href:
                        continue

                    absolute_url = normalize_url(urllib.parse.urljoin(current_url, href))
                    if not absolute_url or not same_domain(absolute_url, source_url):
                        continue
                    if stop_on_last_seen and last_seen_url and absolute_url == last_seen_url:
                        stop_reached = True
                        break

                    score = score_link(absolute_url, str(link.get("text") or ""), str(target.get("name") or ""), rule, extraction_mode) + 2
                    if score < candidate_score_threshold():
                        continue

                    if newest_url is None:
                        newest_url = absolute_url
                    target_candidates.append(
                        {
                            "url": absolute_url,
                            "title": str(link.get("text") or "").strip(),
                            "description": str(target.get("name") or "").strip(),
                            "score": score,
                            "published_at": infer_published_at_from_url(absolute_url),
                            "discovery_method": "category_page",
                        }
                    )

                    if len(target_candidates) >= per_target_limit:
                        break

                if stop_reached or len(target_candidates) >= per_target_limit or not next_url:
                    break

                current_url = next_url

            update_category_target(
                target_id,
                {
                    "last_checked_at": now_iso(),
                    "last_seen_url": newest_url or target.get("last_seen_url"),
                    "last_error": None,
                    "error_type": None,
                    "detected_at": None,
                },
            )
            collected.extend(target_candidates)
        except Exception as exc:
            update_category_target(
                target_id,
                {
                    "last_checked_at": now_iso(),
                    "last_error": str(exc),
                    "error_type": "category_fetch_error",
                    "detected_at": now_iso(),
                },
            )
            failed_targets += 1
            print(f"[discover] Category target failed for {source_name}: {current_url} ({exc})", file=sys.stderr)

    if attempted_targets == 0:
        return None
    if failed_targets == attempted_targets and not collected:
        raise RuntimeError(f"All category targets failed for {source_name}")

    collected.sort(key=lambda item: (-item["score"], item.get("published_at") or "", item.get("url", "")), reverse=True)
    return collected[:limit]


def lookup_existing_article(url: str) -> Optional[dict]:
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    if not supabase_url or not supabase_key:
        return None

    select_fields = "id,published_at,last_scraped_at,content_hash,title"
    normalized_url = normalize_url(url)
    encoded_normalized_url = urllib.parse.quote(normalized_url, safe="")
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/articles?normalized_url=eq.{encoded_normalized_url}&select={select_fields}&limit=1",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        if isinstance(data, list) and len(data) > 0:
            return data[0]
    except urllib.error.HTTPError:
        pass

    encoded_url = urllib.parse.quote(url, safe="")
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/articles?url=eq.{encoded_url}&select={select_fields}&limit=1",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        if isinstance(data, list) and len(data) > 0:
            return data[0]
    except urllib.error.HTTPError:
        return None
    return None


def should_refresh_article(existing_article: dict) -> bool:
    if not env_bool("REFRESH_ENABLED", False):
        return False

    refresh_window_days = env_int("REFRESH_WINDOW_DAYS", 0, 0)
    refresh_cadence_hours = env_int("REFRESH_CADENCE_HOURS", 24, 1)
    if refresh_window_days <= 0:
        return False

    published_at = parse_datetime(str(existing_article.get("published_at") or ""))
    if not published_at:
        return False
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    else:
        published_at = published_at.astimezone(timezone.utc)

    now = datetime.now(timezone.utc)
    if now - published_at > timedelta(days=refresh_window_days):
        return False

    last_scraped_at = parse_datetime(str(existing_article.get("last_scraped_at") or ""))
    if last_scraped_at:
        if last_scraped_at.tzinfo is None:
            last_scraped_at = last_scraped_at.replace(tzinfo=timezone.utc)
        else:
            last_scraped_at = last_scraped_at.astimezone(timezone.utc)
        if now - last_scraped_at < timedelta(hours=refresh_cadence_hours):
            return False

    return True


def is_non_article(url: str, rule: SourceRule) -> bool:
    if any(re.search(pattern, url, re.IGNORECASE) for pattern in rule.non_article_exceptions):
        return False
    patterns = tuple(NON_ARTICLE_PATTERNS) + tuple(rule.exclude_regexes)
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in patterns)


def score_link(url: str, title: str, description: str, rule: SourceRule, mode: str) -> int:
    score = 0
    lower_url = url.lower()
    text = f"{title} {description}".strip()

    if any(pattern.search(url) for pattern in DATE_PATTERNS):
        score += date_score_bonus()
    if any(keyword in lower_url for keyword in ARTICLE_KEYWORDS):
        score += 5
    if any(keyword.lower() in lower_url for keyword in rule.include_keywords):
        score += 5
    if any(re.search(pattern, url, re.IGNORECASE) for pattern in rule.include_regexes):
        score += 7

    if mode == "article_listing" and "/articles/" in lower_url:
        score += 4
    if mode == "rss_feed" and ("/abs/" in lower_url or "/doi/" in lower_url or "/content/10.1101/" in lower_url):
        score += rss_strict_bonus()
    if mode == "rss_feed":
        strict_match = any(keyword.lower() in lower_url for keyword in rule.include_keywords) or any(
            re.search(pattern, url, re.IGNORECASE) for pattern in rule.include_regexes
        )
        if not strict_match:
            score -= 20

    if len(title) >= 25:
        score += 2
    if len(description) >= 25:
        score += 1
    if is_non_article(url, rule):
        score -= 20
    if not text:
        score -= 1
    return score


def recency_key(url: str) -> tuple:
    match = DATE_CAPTURE.search(url)
    if not match:
        return (0, 0, 0)
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3) or "0")
    return (year, month, day)


def discover(source_name: str, source_url: str, extraction_mode: str, limit: int) -> tuple[List[dict], str]:
    rule = SOURCE_RULES.get(source_name, SourceRule())
    source_settings = manifest_source_settings(source_name)
    state = read_source_state()
    category_targets = read_category_targets()

    primary_surface = source_settings.get("primary_discovery_surface") or "map"
    fallback_surface = source_settings.get("fallback_discovery_surface") or "map"
    surfaces = [primary_surface]
    if fallback_surface not in surfaces:
        surfaces.append(fallback_surface)
    if category_targets and "category_page" not in surfaces:
        if "map" in surfaces:
            surfaces.insert(surfaces.index("map"), "category_page")
        else:
            surfaces.append("category_page")
    if "map" not in surfaces:
        surfaces.append("map")

    candidates: List[dict] = []
    used_surface = None
    last_error: Exception | str | None = None
    for surface in surfaces:
        if source_in_cooldown(state, surface) and surface != "map":
            continue
        try:
            if surface == "rss" and source_settings.get("feed_url"):
                candidates = feed_candidates(source_settings["feed_url"], limit, state, rule, extraction_mode)
            elif surface == "sitemap":
                candidates = sitemap_candidates(source_name, limit, state, rule, extraction_mode)
            elif surface == "category_page":
                category_candidates = category_page_candidates(
                    source_name,
                    source_url,
                    limit,
                    rule,
                    extraction_mode,
                    category_targets,
                    force_targets=(surface == primary_surface),
                )
                if category_candidates is None:
                    continue
                candidates = category_candidates
            else:
                discovery_url = rule.discovery_url or source_url
                raw_links = firecrawl_map(discovery_url, rule.map_search, rule.sitemap, configured_map_limit(limit))
                provisional = []
                for item in raw_links:
                    url = item.get("url", "").strip()
                    if not url:
                        continue
                    score = score_link(url, (item.get("title") or "").strip(), (item.get("description") or "").strip(), rule, extraction_mode)
                    if score < candidate_score_threshold():
                        continue
                    provisional.append({
                        "url": url,
                        "title": (item.get("title") or "").strip(),
                        "description": (item.get("description") or "").strip(),
                        "score": score,
                        "published_at": None,
                        "discovery_method": "map",
                    })
                candidates = provisional[:limit]

            used_surface = surface
            break
        except Exception as exc:  # pragma: no cover - network fallback path
            last_error = exc
            mark_surface_failure(surface, exc)
            continue

    if used_surface is None:
        raise RuntimeError(str(last_error or "No discovery surface available"))

    seen = set()
    filtered_candidates = []
    latest_published_at: Optional[str] = None
    for item in candidates:
        url = normalize_url(item.get("url", "").strip())
        if not url or url in seen:
            continue
        seen.add(url)

        existing_article = lookup_existing_article(url)
        processing_lane = "new"
        existing_article_id = None
        existing_content_hash = None
        if existing_article:
            if not should_refresh_article(existing_article):
                continue
            processing_lane = "refresh"
            existing_article_id = existing_article.get("id")
            existing_content_hash = existing_article.get("content_hash")

        published_at = item.get("published_at") or (existing_article or {}).get("published_at")
        if published_at and (latest_published_at is None or published_at > latest_published_at):
            latest_published_at = published_at

        filtered_candidates.append(
            {
                "url": url,
                "title": (item.get("title") or "").strip(),
                "description": (item.get("description") or "").strip(),
                "score": item.get("score", 0),
                "published_at": published_at,
                "discovery_method": item.get("discovery_method", used_surface),
                "processing_lane": processing_lane,
                "existing_article_id": existing_article_id,
                "existing_content_hash": existing_content_hash,
            }
        )

    filtered_candidates.sort(key=lambda item: (-item["score"], item.get("published_at") or "", -recency_key(item["url"])[0], -recency_key(item["url"])[1], -recency_key(item["url"])[2], item["url"]))

    state_patch: dict = {}
    if used_surface == "rss":
        if latest_published_at:
            state_patch["last_cursor_published_at"] = latest_published_at
        if filtered_candidates:
            state_patch["last_cursor_url"] = filtered_candidates[0]["url"]
    if used_surface == "map":
        state_patch["last_map_at"] = now_iso()
    if used_surface == "sitemap":
        state_patch["last_sitemap_checkpoint"] = {url: now_iso() for url in (source_settings.get("sitemap_urls") or recent_nature_article_sitemaps() if source_name == "Nature Biotechnology" else [])}
    if used_surface == "category_page" and filtered_candidates:
        state_patch["last_cursor_url"] = filtered_candidates[0]["url"]
        if latest_published_at:
            state_patch["last_cursor_published_at"] = latest_published_at
    mark_surface_success(used_surface, state_patch)

    return filtered_candidates[:limit], used_surface


def main(argv: Sequence[str]) -> int:
    if len(argv) != 5:
        print(
            json.dumps(
                {
                    "error": "usage: _discover_article_urls.py <source_name> <source_url> <extraction_mode> <limit>"
                }
            )
        )
        return 1

    source_name, source_url, extraction_mode, raw_limit = argv[1:5]
    limit = int(raw_limit)
    try:
        candidates, used_surface = discover(source_name, source_url, extraction_mode, limit)
    except Exception as exc:  # pragma: no cover - shell entrypoint fallback
        print(json.dumps({"error": str(exc), "candidates": []}))
        return 1

    print(
        json.dumps(
            {
                "source_name": source_name,
                "source_url": source_url,
                "extraction_mode": extraction_mode,
                "discovery_surface_used": used_surface,
                "candidate_count": len(candidates),
                "candidates": candidates,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))