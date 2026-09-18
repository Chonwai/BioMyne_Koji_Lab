"""Crawler provider abstraction layer.

Allows the pipeline to switch between local Crawl4AI and Firecrawl Cloud
without changing call sites. See docs/phase1/crawl4ai-migration-engineering-spec.md §4.
"""

from __future__ import annotations

import dataclasses
import os
import xml.etree.ElementTree as ET
from typing import Protocol, runtime_checkable
import urllib.request
import urllib.error
import urllib.parse
import json
import time
import asyncio

# hash_markdown: canonical text normalization (shared by both providers)
try:
    from _pipeline_normalization import hash_markdown
except ModuleNotFoundError:
    from ops.scripts._pipeline_normalization import hash_markdown

# Paywall detection (canonical home; _scrape_markdown.py re-exports these symbols)
PAYWALL_MARKERS = (
    ("sign up to read this article for free", "signup_gate"),
    ("become a premium subscriber", "premium_gate"),
    ("purchase this article", "purchase_gate"),
    ("already a subscriber? [log in]", "subscriber_login_gate"),
    ("just want immediate access to this one article? purchase it now", "purchase_gate"),
)


def detect_paywall(markdown: str) -> tuple[bool, str | None]:
    lowered = markdown.lower()
    for marker, signal in PAYWALL_MARKERS:
        if marker in lowered:
            return True, signal
    return False, None


@dataclasses.dataclass
class ScrapeResult:
    """Structured result of a single scrape (spec §4.4)."""

    success: bool
    markdown: str = ""
    word_count: int = 0
    content_hash: str | None = None
    paywall_detected: bool = False
    paywall_signal: str | None = None
    provider: str = "local"
    firecrawl_timeout_ms: int | None = None  # Firecrawl-only; None for local
    error: str | None = None

@runtime_checkable
class CrawlerProvider(Protocol):
    """Abstract interface for web scraping providers (spec §4.1)."""

    async def scrape(self, url: str) -> ScrapeResult:
        """Scrape a single URL and return structured result.
        - LocalCrawl4AIProvider: natively async (AsyncWebCrawler.arun).
        - FirecrawlProvider: wraps the synchronous Firecrawl HTTP call via asyncio.to_thread.
        """
        ...

    def map(self, url: str, *, search: str | None = None, limit: int = 50) -> list[dict]:
        """Discover candidate article URLs from a page/sitemap.
        Returns list of dicts with keys: url, title (if available), source (provider name).
        """
        ...


class LocalCrawl4AIProvider:
    """Local Playwright + Crawl4AI implementation (spec §4.2)."""

    provider_name = "local"

    async def scrape(self, url: str) -> ScrapeResult:
        """Scrape a single URL using Crawl4AI's AsyncWebCrawler."""
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, DefaultMarkdownGenerator, PruningContentFilter
        except ImportError as exc:
            return ScrapeResult(
                success=False,
                error=f"crawl4ai not installed: {exc}",
                provider=self.provider_name,
            )

        browser_cfg = BrowserConfig(headless=True)
        run_cfg = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.5)
            ),
            cache_mode=CacheMode.BYPASS,
        )

        try:
            async with AsyncWebCrawler(config=browser_cfg) as crawler:
                crawl_result = await crawler.arun(url=url, config=run_cfg)
                markdown = getattr(crawl_result, "markdown", "") or ""
                success = bool(getattr(crawl_result, "success", False))
                error = getattr(crawl_result, "error_message", None) if not success else None

                # Compute paywall detection
                paywall_detected, paywall_signal = detect_paywall(markdown) if success else (False, None)

                return ScrapeResult(
                    success=success,
                    markdown=markdown,
                    word_count=len(markdown.split()),
                    content_hash=hash_markdown(markdown) if success else None,
                    paywall_detected=paywall_detected,
                    paywall_signal=paywall_signal,
                    provider=self.provider_name,
                    error=error,
                )
        except Exception as exc:
            return ScrapeResult(
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                provider=self.provider_name,
            )

    def map(self, url: str, *, search: str | None = None, limit: int = 50) -> list[dict]:
        """Discover article URLs by parsing sitemap XML.
        
        Tries the given URL first; if it fails or isn't valid XML, appends '/sitemap.xml'.
        Returns list of dicts with keys: url, title (empty), source ("local").
        """
        # Candidates: try the URL directly, then url/sitemap.xml
        candidates = [url]
        if not url.endswith(".xml"):
            candidates.append(url.rstrip("/") + "/sitemap.xml")

        for sitemap_url in candidates:
            try:
                req = urllib.request.Request(sitemap_url, headers={"User-Agent": "BioMyne-Koji/1.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                    root = ET.fromstring(data)
                    # Handle both <loc> and <url><loc> patterns
                    locs = []
                    # Try namespace-agnostic search first (Crawl4AI sitemap format)
                    for loc in root.iter():
                        if loc.tag.endswith("}loc") or loc.tag == "loc":
                            text = (loc.text or "").strip()
                            if text:
                                locs.append(text)
                    # If no locs found, try standard <url><loc> structure
                    if not locs:
                        for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                            loc_elem = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                            if loc_elem is not None and loc_elem.text:
                                locs.append(loc_elem.text.strip())
                    # Build result
                    results = [{"url": loc, "title": "", "source": self.provider_name} for loc in locs[:limit]]
                    if results:
                        return results
            except (urllib.error.URLError, ET.ParseError, Exception) as exc:
                # Log but continue to next candidate
                import sys
                print(f"[map] sitemap load failed for {sitemap_url}: {exc}", file=sys.stderr)
                continue
        return []


class FirecrawlProvider:
    """Firecrawl Cloud implementation (spec §4.2)."""

    provider_name = "firecrawl_cloud"

    async def scrape(self, url: str) -> ScrapeResult:
        """Scrape via Firecrawl /v1/scrape (spec §4.2), wrapped in to_thread."""
        token = os.environ.get("FIRECRAWL_KEY") or os.environ.get("FIRECRAWL_API_KEY")
        if not token:
            return ScrapeResult(success=False, error="FIRECRAWL_KEY or FIRECRAWL_API_KEY is required", provider="firecrawl_cloud")
        return await asyncio.to_thread(self._scrape_sync, url, token)

    def _scrape_sync(self, url: str, token: str) -> ScrapeResult:
        # Logic mirrors _scrape_markdown.py L79-112
        def env_int(name: str, default: int, minimum: int = 0) -> int:
            raw = os.environ.get(name, "").strip()
            if not raw: return max(default, minimum)
            try: value = int(raw)
            except ValueError: value = default
            return max(value, minimum)

        def scrape_timeout_ms(url: str, attempt: int) -> int:
            base = env_int("FIRECRAWL_SCRAPE_TIMEOUT_MS", 120000, 30000)
            step = env_int("FIRECRAWL_SCRAPE_TIMEOUT_STEP_MS", 30000, 0)
            bonus_base = env_int("FIRECRAWL_SCRAPE_SCHOLARLY_TIMEOUT_BONUS_MS", 60000, 0)
            host = urllib.parse.urlparse(url).netloc.lower()
            bonus = bonus_base if any(d in host for d in ("biorxiv.org", "medrxiv.org", "arxiv.org")) else 0
            return base + bonus + (attempt * step)

        retryable = {408, 409, 425, 429, 500, 502, 503, 504}
        max_attempts = env_int("FIRECRAWL_SCRAPE_ATTEMPTS", 4, 1)
        last_error = None

        for attempt in range(max_attempts):
            timeout_ms = scrape_timeout_ms(url, attempt)
            payload = {
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True,
                "timeout": timeout_ms,
                "waitFor": 2000,
            }
            req = urllib.request.Request(
                "https://api.firecrawl.dev/v1/scrape",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=max(90, (timeout_ms // 1000) + 30)) as resp:
                    data = json.loads(resp.read())
                if not data.get("success"):
                    last_error = json.dumps(data)
                    if attempt == max_attempts - 1: break
                    time.sleep(2 ** attempt)
                    continue
                
                markdown = data.get("data", {}).get("markdown", "")
                paywall_detected, paywall_signal = detect_paywall(markdown)
                return ScrapeResult(
                    success=True,
                    markdown=markdown,
                    word_count=len(markdown.split()),
                    content_hash=hash_markdown(markdown),
                    paywall_detected=paywall_detected,
                    paywall_signal=paywall_signal,
                    provider="firecrawl_cloud",
                    firecrawl_timeout_ms=timeout_ms
                )
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
                last_error = f"HTTP {exc.code}: {body or exc.reason}"
                if exc.code not in retryable or attempt == max_attempts - 1: break
                time.sleep(2 ** attempt)
            except Exception as exc:
                last_error = str(exc)
                if attempt == max_attempts - 1: break
                time.sleep(2 ** attempt)

        return ScrapeResult(
            success=False,
            error=last_error or "Unknown Firecrawl scrape failure",
            provider="firecrawl_cloud"
        )

    def map(self, url: str, *, search: str | None = None, limit: int = 50) -> list[dict]:
        """Discover URLs via Firecrawl /v2/map (spec §4.2), wrapped in to_thread."""
        token = os.environ.get("FIRECRAWL_KEY") or os.environ.get("FIRECRAWL_API_KEY")
        if not token:
            return []
        return asyncio.run(asyncio.to_thread(self._map_sync, url, token, search, limit))

    def _map_sync(self, url: str, token: str, search: str | None, limit: int) -> list[dict]:
        # Logic mirrors _discover_article_urls.py firecrawl_map L225-269
        def env_int(name: str, default: int, minimum: int = 0) -> int:
            raw = os.environ.get(name, "").strip()
            if not raw: return max(default, minimum)
            try: value = int(raw)
            except ValueError: value = default
            return max(value, minimum)

        timeout_ms = env_int("DISCOVERY_MAP_TIMEOUT_MS", 90000)
        retry_attempts = env_int("DISCOVERY_MAP_RETRY_ATTEMPTS", 5)
        retryable = {408, 409, 425, 429, 500, 502, 503, 504}

        # Mirrors _discover_article_urls.py firecrawl_map(): when the url is a
        # sitemap itself, pass it as the sitemap param; otherwise let Firecrawl infer.
        sitemap = url if (url.lower().endswith(".xml") or "sitemap" in url.lower()) else None
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
                if exc.code not in retryable or attempt == retry_attempts - 1: raise
                time.sleep(2 ** attempt)
            except Exception as exc:
                last_error = exc
                if attempt == retry_attempts - 1: raise
                time.sleep(2 ** attempt)
        
        links = data.get("links", [])
        if not isinstance(links, list):
            return []
        return [{"url": l, "title": "", "source": "firecrawl_cloud"} for l in links]


def create_provider(name: str | None = None) -> CrawlerProvider:
    """Factory (spec §4.3 / Step 2).

    Reads CRAWLER_PROVIDER env (default "local"). Accepts an explicit name override.
    """
    provider_name = name or os.environ.get("CRAWLER_PROVIDER", "local")
    if provider_name == "firecrawl_cloud":
        return FirecrawlProvider()
    return LocalCrawl4AIProvider()