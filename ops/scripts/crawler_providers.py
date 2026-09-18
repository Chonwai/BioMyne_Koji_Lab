"""Crawler provider abstraction layer.

Allows the pipeline to switch between local Crawl4AI and Firecrawl Cloud
without changing call sites. See docs/phase1/crawl4ai-migration-engineering-spec.md §4.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Protocol, runtime_checkable


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
        """TODO(P1 Step 2): implement with AsyncWebCrawler."""
        raise NotImplementedError("LocalCrawl4AIProvider.scrape — implement in P1 Step 2")

    def map(self, url: str, *, search: str | None = None, limit: int = 50) -> list[dict]:
        """TODO(P1 Step 2): implement with Crawl4AI link discovery or sitemap XML parse."""
        raise NotImplementedError("LocalCrawl4AIProvider.map — implement in P1 Step 2")


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