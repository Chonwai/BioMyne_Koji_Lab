#!/usr/bin/env python3
"""Discover candidate article URLs for a source via Firecrawl /v2/map.

This helper keeps the shell pipeline small and makes source-specific URL
discovery testable in isolation.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence


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


@dataclass(frozen=True)
class SourceRule:
    discovery_url: Optional[str] = None
    map_search: Optional[str] = None
    sitemap: str = "include"
    include_keywords: Sequence[str] = ()
    include_regexes: Sequence[str] = ()
    exclude_regexes: Sequence[str] = ()


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
        include_keywords=("/news/", "/topics/"),
        exclude_regexes=(r"/topics/[^/]+/$",),
    ),
    "Endpoints News": SourceRule(
        include_keywords=("/202", "/news/", "/biotech/", "/pharma/"),
    ),
    "BioCentury": SourceRule(
        include_keywords=("/article/", "/biopharma/", "/business/"),
    ),
    "SynBioBeta": SourceRule(
        include_keywords=("/read/", "/article/"),
    ),
    "arXiv Quantitative Biology": SourceRule(
        discovery_url="https://arxiv.org/list/q-bio/new",
        map_search="abs",
        sitemap="skip",
        include_keywords=("/abs/",),
        exclude_regexes=(r"/archive/", r"/list/"),
    ),
    "bioRxiv": SourceRule(
        discovery_url="https://www.biorxiv.org/content/early/recent",
        map_search="content/10.1101",
        sitemap="skip",
        include_regexes=(r"/content/10\.1101/",),
    ),
    "Science": SourceRule(
        discovery_url="https://www.science.org/toc/science/current",
        map_search="doi",
        sitemap="skip",
        include_keywords=("/doi/",),
    ),
}


def firecrawl_map(url: str, search: Optional[str], sitemap: str, limit: int) -> List[dict]:
    token = os.environ.get("FIRECRAWL_KEY") or os.environ.get("FIRECRAWL_API_KEY")
    if not token:
        raise RuntimeError("FIRECRAWL_KEY or FIRECRAWL_API_KEY is required")

    payload = {
        "url": url,
        "sitemap": sitemap,
        "includeSubdomains": False,
        "ignoreQueryParameters": True,
        "limit": limit,
        "timeout": 60000,
    }
    if search:
        payload["search"] = search

    last_error = None
    for attempt in range(3):
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
            with urllib.request.urlopen(req, timeout=70) as resp:
                data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in (408, 409, 425, 429, 500, 502, 503, 504) or attempt == 2:
                raise
            time.sleep(2 ** attempt)
        except Exception as exc:
            last_error = exc
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"Firecrawl map failed: {last_error}")

    links = data.get("links", [])
    if not isinstance(links, list):
        return []
    return [item for item in links if isinstance(item, dict) and item.get("url")]


def load_xml_sitemap(url: str) -> List[dict]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "BioMyne-Koji/1.0 (+https://www.biomyne.com)",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read()

    root = ET.fromstring(body)
    namespace_match = re.match(r"\{(.+)\}", root.tag)
    namespace = namespace_match.group(1) if namespace_match else ""
    loc_tag = f"{{{namespace}}}loc" if namespace else "loc"

    links: List[dict] = []
    for loc in root.iter(loc_tag):
        if not loc.text:
            continue
        links.append({"url": loc.text.strip(), "title": "", "description": ""})
    return links


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


def article_exists(url: str) -> bool:
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    if not supabase_url or not supabase_key:
        return False

    encoded_url = urllib.parse.quote(url, safe="")
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/articles?url=eq.{encoded_url}&select=id&limit=1",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return isinstance(data, list) and len(data) > 0
    except urllib.error.HTTPError:
        return False


def is_non_article(url: str, rule: SourceRule) -> bool:
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


def discover(source_name: str, source_url: str, extraction_mode: str, limit: int) -> List[dict]:
    rule = SOURCE_RULES.get(source_name, SourceRule())
    discovery_url = rule.discovery_url or source_url
    raw_links = firecrawl_map(discovery_url, rule.map_search, rule.sitemap, configured_map_limit(limit))

    supplemental_sitemaps: List[str] = []
    if source_name == "Nature Biotechnology":
        supplemental_sitemaps.extend(recent_nature_article_sitemaps())

    for sitemap_url in supplemental_sitemaps:
        try:
            raw_links.extend(load_xml_sitemap(sitemap_url))
        except Exception as exc:
            print(
                f"[discover] Supplemental sitemap load failed for {source_name}: {sitemap_url} ({exc})",
                file=sys.stderr,
            )
            continue

    candidates = []
    seen = set()
    threshold = candidate_score_threshold()
    for item in raw_links:
        url = item.get("url", "").strip()
        if not url or url in seen:
            continue
        seen.add(url)

        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()
        score = score_link(url, title, description, rule, extraction_mode)
        if score < threshold:
            continue
        if article_exists(url):
            continue

        candidates.append(
            {
                "url": url,
                "title": title,
                "description": description,
                "score": score,
            }
        )

    candidates.sort(key=lambda item: (-item["score"], -recency_key(item["url"])[0], -recency_key(item["url"])[1], -recency_key(item["url"])[2], item["url"]))
    return candidates[:limit]


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
        candidates = discover(source_name, source_url, extraction_mode, limit)
    except Exception as exc:  # pragma: no cover - shell entrypoint fallback
        print(json.dumps({"error": str(exc), "candidates": []}))
        return 1

    print(
        json.dumps(
            {
                "source_name": source_name,
                "source_url": source_url,
                "extraction_mode": extraction_mode,
                "candidate_count": len(candidates),
                "candidates": candidates,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))