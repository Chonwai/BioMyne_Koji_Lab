"""Integration tests for crawler_providers (spec §8.2).

These tests hit the real network and are skipped by default.
Run with: RUN_INTEGRATION=1 pytest -m integration
"""

import asyncio
import os
import pytest

from crawler_providers import create_provider, FirecrawlProvider, ScrapeResult

# Spec §8.2: repo default MIN_WORDS_FOR_LLM = 100
MIN_WORDS_FOR_LLM = int(os.environ.get("MIN_WORDS_FOR_LLM", "100"))


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("RUN_INTEGRATION"),
    reason="integration test skipped (set RUN_INTEGRATION=1 to run)",
)
class TestLocalScrapeIntegration:
    """Real-network scrapes using LocalCrawl4AIProvider."""

    def test_local_scrape_biorxiv(self):
        """bioRxiv public page → success=True, word_count ≥ MIN_WORDS_FOR_LLM."""
        provider = create_provider("local")
        result = asyncio.run(
            provider.scrape("https://www.biorxiv.org/content/10.1101/2024.05.21.595135v1")
        )
        assert result.success is True, f"scrape failed: {result.error}"
        assert result.word_count >= MIN_WORDS_FOR_LLM, (
            f"word_count {result.word_count} < MIN_WORDS_FOR_LLM ({MIN_WORDS_FOR_LLM})"
        )
        assert result.content_hash is not None

    def test_local_scrape_statnews(self):
        """STAT News public page → success=True, word_count ≥ MIN_WORDS_FOR_LLM."""
        provider = create_provider("local")
        result = asyncio.run(provider.scrape("https://www.statnews.com/"))
        assert result.success is True, f"scrape failed: {result.error}"
        assert result.word_count >= MIN_WORDS_FOR_LLM, (
            f"word_count {result.word_count} < MIN_WORDS_FOR_LLM ({MIN_WORDS_FOR_LLM})"
        )


class TestFirecrawlProviderNoKey:
    """FirecrawlProvider without FIRECRAWL_KEY → success=False (no API needed)."""

    def test_no_key_returns_failure(self, monkeypatch):
        """No FIRECRAWL_KEY set → scrape returns success=False with non-empty error."""
        monkeypatch.delenv("FIRECRAWL_KEY", raising=False)
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        provider = FirecrawlProvider()
        # scrape is async, so we need asyncio.run
        import asyncio
        result = asyncio.run(provider.scrape("https://example.com"))
        assert isinstance(result, ScrapeResult)
        assert result.success is False
        assert result.error is not None
        assert len(result.error) > 0
