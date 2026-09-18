"""Unit tests for crawler_providers module (spec §8.1)."""

import dataclasses
import pytest

from crawler_providers import (
    ScrapeResult,
    LocalCrawl4AIProvider,
    FirecrawlProvider,
    create_provider,
)
from _pipeline_normalization import hash_markdown
from _scrape_markdown import PAYWALL_MARKERS


# ── 8.1 Unit Tests ──────────────────────────────────────────────


class TestScrapeResultFields:
    """ScrapeResult includes all 7 required fields + 2 optional fields with defaults."""

    def test_required_fields_present(self):
        r = ScrapeResult(success=True)
        # 7 required fields per spec §4.4
        assert hasattr(r, "success")
        assert hasattr(r, "markdown")
        assert hasattr(r, "word_count")
        assert hasattr(r, "content_hash")
        assert hasattr(r, "paywall_detected")
        assert hasattr(r, "paywall_signal")
        assert hasattr(r, "provider")

    def test_required_field_types(self):
        r = ScrapeResult(
            success=True,
            markdown="hello",
            word_count=1,
            content_hash="abc",
            paywall_detected=False,
            paywall_signal=None,
            provider="local",
        )
        assert isinstance(r.success, bool)
        assert isinstance(r.markdown, str)
        assert isinstance(r.word_count, int)
        assert isinstance(r.provider, str)

    def test_optional_fields_have_defaults(self):
        r = ScrapeResult(success=True)
        # firecrawl_timeout_ms defaults to None (local provider)
        assert r.firecrawl_timeout_ms is None
        # error defaults to None
        assert r.error is None

    def test_optional_fields_accept_values(self):
        r = ScrapeResult(success=False, error="timeout", firecrawl_timeout_ms=120000)
        assert r.firecrawl_timeout_ms == 120000
        assert r.error == "timeout"


class TestContentHashStability:
    """Same markdown always produces the same hash (spec §8.1)."""

    def test_stability(self):
        md = "# Title\n\nThis is a test article with enough content."
        h1 = hash_markdown(md)
        h2 = hash_markdown(md)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex digest

    def test_different_content_different_hash(self):
        h1 = hash_markdown("alpha bravo charlie")
        h2 = hash_markdown("delta echo foxtrot")
        assert h1 != h2

    def test_whitespace_insensitive(self):
        h1 = hash_markdown("hello   world")
        h2 = hash_markdown("hello world")
        assert h1 == h2


class TestPaywallDetection:
    """PAYWALL_MARKERS in markdown trigger paywall detection (spec §8.1)."""

    def test_paywall_detected(self):
        # Import the real detect_paywall
        from _scrape_markdown import detect_paywall
        for marker, expected_signal in PAYWALL_MARKERS:
            sample = f"Please {marker} to continue reading this article."
            detected, signal = detect_paywall(sample)
            assert detected is True, f"Failed to detect paywall marker: {marker}"
            assert signal == expected_signal

    def test_clean_article_no_paywall(self):
        from _scrape_markdown import detect_paywall
        clean = "This is an open access article with no paywall restrictions."
        detected, signal = detect_paywall(clean)
        assert detected is False
        assert signal is None

    def test_empty_markdown_no_paywall(self):
        from _scrape_markdown import detect_paywall
        detected, signal = detect_paywall("")
        assert detected is False


class TestProviderFactory:
    """create_provider() returns the correct provider type (spec §8.1)."""

    def test_local_provider(self):
        p = create_provider("local")
        assert isinstance(p, LocalCrawl4AIProvider)

    def test_firecrawl_provider(self):
        p = create_provider("firecrawl_cloud")
        assert isinstance(p, FirecrawlProvider)

    def test_default_is_local(self):
        p = create_provider()
        assert isinstance(p, LocalCrawl4AIProvider)

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("CRAWLER_PROVIDER", "firecrawl_cloud")
        p = create_provider()
        assert isinstance(p, FirecrawlProvider)
