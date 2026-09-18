"""Unit tests for crawler_providers module (spec §8.1)."""

import asyncio
import dataclasses
import json
import time
import urllib.error

import pytest

from crawler_providers import (
    ScrapeResult,
    LocalCrawl4AIProvider,
    FirecrawlProvider,
    create_provider,
)
from _pipeline_normalization import hash_markdown
from _scrape_markdown import PAYWALL_MARKERS


class _FakeHTTPResponse:
    """Minimal urlopen-compatible response (context manager + read)."""

    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


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


class TestHashStabilityBoilerplate:
    """P2 F-2: boilerplate exclusion makes hashes stable across requests.

    Three known dynamic-element drift sources must not affect the hash:
      1. Nature: `_csrf` CSRF token in URLs (changes every request)
      2. STAT:   OneTrust cookie-consent modal (randomly kept by PruningContentFilter)
      3. GEN:    ADVERTISEMENT / SCROLL TO CONTINUE ad-slot lines (random)
    """

    # ── 1. _csrf CSRF token (Nature) ──

    def test_hash_stability_csrf(self):
        base = (
            "# Article title\n\n"
            "Some stable paragraph about biotech.\n\n"
            "[ Save article ](https://www.nature.com/articles/s41587-026-03333-8/save-research?_csrf=abc123)\n\n"
            "More content here.\n"
        )
        variant = base.replace("_csrf=abc123", "_csrf=xyz789")
        assert hash_markdown(base) == hash_markdown(variant)

    def test_csrf_removal_keeps_link_text(self):
        """Only the query is stripped; the link text survives (no false positive)."""
        md = "[ Save article ](https://www.nature.com/articles/x/save-research?_csrf=tok123)"
        normalized = __import__("_pipeline_normalization", fromlist=["normalize_markdown_for_hash"])
        out = normalized.normalize_markdown_for_hash(md)
        assert "_csrf" not in out
        assert "save article" in out

    # ── 2. OneTrust cookie-consent modal (STAT) ──

    def test_hash_stability_cookie_modal(self):
        without = (
            "# STAT article\n\n"
            "The lead paragraph of the story.\n\n"
            "A second stable paragraph with real reporting.\n"
        )
        modal = (
            "![STAT News](https://cdn.cookielaw.org/logos/static/ot_company_logo.png)\n"
            "## Privacy Preference Center\n"
            "When you visit any website, it may store or retrieve information on your browser.\n"
            "[More information](https://cookiepedia.co.uk/giving-consent-to-cookies)\n"
            "Allow All\n"
            "### Manage Consent Preferences\n"
            "#### Strictly Necessary Cookies\n"
            "#### Targeting Cookies\n"
            "#### Performance Cookies\n"
            "#### Functional Cookies\n"
            "### Cookie List\n"
            "Apply\n"
            "Cancel\n"
            "Reject All\n"
            "Confirm My Choices\n"
            "[![Powered by Onetrust](...)](https://www.onetrust.com/products/cookie-consent/)\n"
        )
        with_modal = modal + without
        assert hash_markdown(with_modal) == hash_markdown(without)

    def test_cookie_modal_header_stripped(self):
        """A realistic full modal (with terminal END marker) is removed wholesale;
        body AFTER the modal survives."""
        md = (
            "![STAT News](https://cdn.cookielaw.org/logos/static/ot_company_logo.png)\n"
            "## Privacy Preference Center\n"
            "When you visit any website, it may store or retrieve information.\n"
            "[More information](https://cookiepedia.co.uk/giving-consent-to-cookies)\n"
            "Allow All\n"
            "Confirm My Choices\n"
            "[![Powered by Onetrust](...)](https://www.onetrust.com/products/cookie-consent/)\n"
            "Some body text.\n"
        )
        out = __import__("_pipeline_normalization", fromlist=["normalize_markdown_for_hash"])
        normalized = out.normalize_markdown_for_hash(md)
        assert "privacy preference center" not in normalized
        assert "cookiepedia" not in normalized
        assert "onetrust" not in normalized
        assert "some body text" in normalized

    def test_truncated_modal_cap_prevents_swallowing_body(self):
        """Safety cap: a modal without an END marker cannot swallow unbounded
        article prose (MAX_COOKIE_MODAL_LINES = 60)."""
        md = (
            "## Privacy Preference Center\n"
            + "\n".join(f"junk line {i}" for i in range(100))
            + "\nREAL CONTENT LINE\n"
        )
        out = __import__("_pipeline_normalization", fromlist=["normalize_markdown_for_hash"])
        normalized = out.normalize_markdown_for_hash(md)
        # beyond the cap the lines are preserved (not swallowed)
        assert "junk line 99" in normalized
        assert "real content line" in normalized
        # exactly the cap worth of lines is dropped (header + junk 0..58
        # consumed; use non-substring-colliding line numbers)
        assert "junk line 58" not in normalized
        assert "junk line 59" in normalized

    def test_nature_cookie_banner_stripped(self):
        """Nature 'Your privacy, your choice' banner (fit-region drift source)
        is removed while article body survives."""
        md = (
            "## Your privacy, your choice\n"
            "We use essential cookies to make sure the site can function. We also use optional cookies.\n"
            "By accepting optional cookies, you consent to the processing of your personal data.\n"
            "See our [privacy policy](https://www.nature.com/info/privacy) for more information.\n"
            "Accept all cookies Reject optional cookies\n"
            "Article body text that must survive.\n"
        )
        out = __import__("_pipeline_normalization", fromlist=["normalize_markdown_for_hash"])
        normalized = out.normalize_markdown_for_hash(md)
        assert "your privacy" not in normalized
        assert "cookies" not in normalized
        assert "nature.com/info/privacy" not in normalized
        assert "article body text" in normalized

    def test_sage_cookie_banner_stripped(self):
        """GEN (Sage) 'Accept Non-Essential Cookies' banner (fit-region drift
        source) is removed while article body survives."""
        md = (
            'By clicking "Accept Non-Essential Cookies", you agree to the storing of cookies on your device.\n'
            "Manage Cookies\n"
            "Reject Non-Essential Cookies Accept Non-Essential Cookies\n"
            "Article body text that must survive.\n"
        )
        out = __import__("_pipeline_normalization", fromlist=["normalize_markdown_for_hash"])
        normalized = out.normalize_markdown_for_hash(md)
        assert "non-essential cookies" not in normalized
        assert "manage cookies" not in normalized
        assert "article body text" in normalized

    # ── 3. ADVERTISEMENT / SCROLL TO CONTINUE (GEN) ──

    def test_hash_stability_advertisement(self):
        without = (
            "# GEN article\n\n"
            "The main article text with substantive content.\n\n"
            "Continuing paragraphs that define the story.\n"
        )
        with_ad = (
            "ADVERTISEMENT\n"
            "SCROLL TO CONTINUE WITH CONTENT\n"
            + without
        )
        assert hash_markdown(with_ad) == hash_markdown(without)

    def test_advertisement_line_removed(self):
        """Standalone ADVERTISEMENT / SCROLL lines are removed; body kept."""
        md = "ADVERTISEMENT\nSome body content remains.\nSCROLL TO CONTINUE WITH CONTENT\n"
        out = __import__("_pipeline_normalization", fromlist=["normalize_markdown_for_hash"])
        normalized = out.normalize_markdown_for_hash(md)
        assert "advertisement" not in normalized
        assert "some body content remains" in normalized

    # ── regression: legacy 6-step normalization untouched ──

    def test_legacy_normalization_still_applies(self):
        """Boilerplate exclusion must not break the original 6-step rules."""
        md = "  Title   Line\n\nSome<!-- comment -->body  text\r\n"
        out = __import__("_pipeline_normalization", fromlist=["normalize_markdown_for_hash"])
        normalized = out.normalize_markdown_for_hash(md)
        assert "<!--" not in normalized
        assert "  " not in normalized  # no double spaces
        assert "somebody text" in normalized  # comment removed → Somebody


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


# ── F-3 additions: map() + retry coverage ──────────────────────

SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/article/one</loc></url>
  <url><loc>https://example.com/article/two</loc></url>
  <url><loc>https://example.com/article/three</loc></url>
</urlset>
"""


class TestProviderMap:
    """LocalCrawl4AIProvider.map parses sitemap XML (spec §8.1)."""

    def test_map_parses_sitemap_xml(self, monkeypatch):
        requests = []

        def fake_urlopen(req, timeout=None):
            requests.append(req)
            return _FakeHTTPResponse(SITEMAP_XML.encode("utf-8"))

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        links = LocalCrawl4AIProvider().map("https://example.com/sitemap.xml")

        assert [item["url"] for item in links] == [
            "https://example.com/article/one",
            "https://example.com/article/two",
            "https://example.com/article/three",
        ]
        assert all(item["source"] == "local" for item in links)
        assert len(requests) == 1  # direct .xml URL never falls back

    def test_map_respects_limit(self, monkeypatch):
        monkeypatch.setattr(
            "urllib.request.urlopen",
            lambda req, timeout=None: _FakeHTTPResponse(SITEMAP_XML.encode("utf-8")),
        )
        links = LocalCrawl4AIProvider().map("https://example.com/sitemap.xml", limit=2)
        assert [item["url"] for item in links] == [
            "https://example.com/article/one",
            "https://example.com/article/two",
        ]

    def test_map_falls_back_to_sitemap_path(self, monkeypatch):
        requested = []

        def fake_urlopen(req, timeout=None):
            requested.append(req.full_url)
            if req.full_url.endswith("/sitemap.xml"):
                return _FakeHTTPResponse(SITEMAP_XML.encode("utf-8"))
            raise urllib.error.URLError("not a sitemap")

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        links = LocalCrawl4AIProvider().map("https://example.com")

        assert requested == ["https://example.com", "https://example.com/sitemap.xml"]
        assert len(links) == 3

    def test_map_returns_empty_list_when_all_candidates_fail(self, monkeypatch):
        def fake_urlopen(req, timeout=None):
            raise urllib.error.URLError("offline")

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        assert LocalCrawl4AIProvider().map("https://example.com") == []

    def test_firecrawl_map_passes_sitemap_mode_and_normalizes_links(self, monkeypatch):
        monkeypatch.setenv("FIRECRAWL_KEY", "test-token")
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured.update(json.loads(req.data.decode("utf-8")))
            body = {
                "success": True,
                "links": [
                    {"url": "https://example.com/article/one", "title": "One", "description": "First"},
                    "https://example.com/article/two",
                ],
            }
            return _FakeHTTPResponse(json.dumps(body).encode("utf-8"))

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        links = FirecrawlProvider().map("https://example.com", search="content/10.", limit=25, sitemap="skip")

        assert captured["sitemap"] == "skip"
        assert captured["search"] == "content/10."
        assert captured["limit"] == 25
        assert [item["url"] for item in links] == [
            "https://example.com/article/one",
            "https://example.com/article/two",
        ]
        assert links[0]["title"] == "One"
        assert links[0]["description"] == "First"
        assert all(item["source"] == "firecrawl_cloud" for item in links)


class TestFirecrawlRetry:
    """FirecrawlProvider retries retryable HTTP errors (spec §8.1)."""

    SCRAPE_OK_BODY = {
        "success": True,
        "data": {"markdown": "# Article\n\n" + ("word " * 60)},
    }

    def _fake_key(self, monkeypatch):
        monkeypatch.setenv("FIRECRAWL_KEY", "test-token")
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        monkeypatch.setattr(time, "sleep", lambda _seconds: None)

    def test_scrape_retries_then_succeeds(self, monkeypatch):
        self._fake_key(monkeypatch)
        monkeypatch.setenv("FIRECRAWL_SCRAPE_ATTEMPTS", "3")
        calls = {"count": 0}
        body = json.dumps(self.SCRAPE_OK_BODY).encode("utf-8")

        def fake_urlopen(req, timeout=None):
            calls["count"] += 1
            if calls["count"] == 1:
                raise urllib.error.HTTPError(req.full_url, 503, "Service Unavailable", None, None)
            return _FakeHTTPResponse(body)

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        result = asyncio.run(FirecrawlProvider().scrape("https://example.com/article"))

        assert result.success is True
        assert result.word_count >= 50
        assert result.content_hash is not None
        assert calls["count"] == 2  # one retry after the 503

    def test_scrape_does_not_retry_non_retryable_error(self, monkeypatch):
        self._fake_key(monkeypatch)
        monkeypatch.setenv("FIRECRAWL_SCRAPE_ATTEMPTS", "3")
        calls = {"count": 0}

        def fake_urlopen(req, timeout=None):
            calls["count"] += 1
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", None, None)

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        result = asyncio.run(FirecrawlProvider().scrape("https://example.com/missing"))

        assert result.success is False
        assert calls["count"] == 1  # 404 is not retryable
        assert "404" in (result.error or "")

    def test_scrape_stops_after_max_attempts(self, monkeypatch):
        self._fake_key(monkeypatch)
        monkeypatch.setenv("FIRECRAWL_SCRAPE_ATTEMPTS", "3")
        calls = {"count": 0}

        def fake_urlopen(req, timeout=None):
            calls["count"] += 1
            raise urllib.error.HTTPError(req.full_url, 503, "Service Unavailable", None, None)

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        result = asyncio.run(FirecrawlProvider().scrape("https://example.com/article"))

        assert result.success is False
        assert calls["count"] == 3  # exactly FIRECRAWL_SCRAPE_ATTEMPTS attempts
        assert "503" in (result.error or "")

    def test_map_retries_then_succeeds(self, monkeypatch):
        self._fake_key(monkeypatch)
        monkeypatch.setenv("DISCOVERY_MAP_RETRY_ATTEMPTS", "3")
        calls = {"count": 0}
        body = json.dumps(
            {"success": True, "links": ["https://example.com/article/one"]}
        ).encode("utf-8")

        def fake_urlopen(req, timeout=None):
            calls["count"] += 1
            if calls["count"] == 1:
                raise urllib.error.HTTPError(req.full_url, 503, "Service Unavailable", None, None)
            return _FakeHTTPResponse(body)

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        links = FirecrawlProvider().map("https://example.com")

        assert [item["url"] for item in links] == ["https://example.com/article/one"]
        assert calls["count"] == 2


class TestDiscoverMapDelegation:
    """_discover_article_urls.firecrawl_map delegates to FirecrawlProvider.map (F-4)."""

    def test_delegates_and_passes_sitemap_mode(self, monkeypatch):
        monkeypatch.setenv("FIRECRAWL_KEY", "test-token")
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured.update(json.loads(req.data.decode("utf-8")))
            body = {"success": True, "links": [{"url": "https://example.com/a", "title": "", "description": ""}]}
            return _FakeHTTPResponse(json.dumps(body).encode("utf-8"))

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

        import _discover_article_urls

        links = _discover_article_urls.firecrawl_map("https://example.com", "content/10.", "skip", 25)

        assert captured["sitemap"] == "skip"
        assert captured["limit"] == 25
        assert [item["url"] for item in links] == ["https://example.com/a"]

    def test_missing_token_raises(self, monkeypatch):
        monkeypatch.delenv("FIRECRAWL_KEY", raising=False)
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)

        import _discover_article_urls

        with pytest.raises(RuntimeError):
            _discover_article_urls.firecrawl_map("https://example.com", None, "include", 10)
