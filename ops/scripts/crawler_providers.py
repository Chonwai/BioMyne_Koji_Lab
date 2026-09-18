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

# Import hash_markdown from the normalization module (same as _scrape_markdown.py)
try:
    from _pipeline_normalization import hash_markdown
except ModuleNotFoundError:
    from ops.scripts._pipeline_normalization import hash_markdown

# Import detect_paywall from _scrape_markdown.py
try:
    from _scrape_markdown import detect_paywall
except ModuleNotFoundError:
    from ops.scripts._scrape_markdown import detect_paywall

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
        """TODO(P1 Step 3): wrap _scrape_markdown.py logic via asyncio.to_thread."""
        raise NotImplementedError("FirecrawlProvider.scrape — implement in P1 Step 3")

    def map(self, url: str, *, search: str | None = None, limit: int = 50) -> list[dict]:
        """TODO(P1 Step 3): call firecrawl_map logic from _discover_article_urls.py."""
        raise NotImplementedError("FirecrawlProvider.map — implement in P1 Step 3")


def create_provider(name: str | None = None) -> CrawlerProvider:
    """Factory (spec §4.3 / Step 2).

    Reads CRAWLER_PROVIDER env (default "local"). Accepts an explicit name override.
    """
    provider_name = name or os.environ.get("CRAWLER_PROVIDER", "local")
    if provider_name == "firecrawl_cloud":
        return FirecrawlProvider()
    return LocalCrawl4AIProvider()