#!/usr/bin/env python3
"""Scrape a single page to markdown via Firecrawl /v1/scrape with retries."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    from _pipeline_normalization import hash_markdown
except ModuleNotFoundError:
    from ops.scripts._pipeline_normalization import hash_markdown


RETRYABLE_HTTP_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
PAYWALL_MARKERS = (
    ("sign up to read this article for free", "signup_gate"),
    ("become a premium subscriber", "premium_gate"),
    ("purchase this article", "purchase_gate"),
    ("already a subscriber? [log in]", "subscriber_login_gate"),
    ("just want immediate access to this one article? purchase it now", "purchase_gate"),
)


def env_int(name: str, default: int, minimum: int = 0) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return max(default, minimum)
    try:
        value = int(raw)
    except ValueError:
        value = default
    return max(value, minimum)


def scrape_timeout_ms(url: str, attempt: int) -> int:
    base_timeout = env_int("FIRECRAWL_SCRAPE_TIMEOUT_MS", 120000, 30000)
    timeout_step = env_int("FIRECRAWL_SCRAPE_TIMEOUT_STEP_MS", 30000, 0)
    scholarly_bonus = env_int("FIRECRAWL_SCRAPE_SCHOLARLY_TIMEOUT_BONUS_MS", 60000, 0)
    host = urllib.parse.urlparse(url).netloc.lower()
    bonus = scholarly_bonus if any(domain in host for domain in ("biorxiv.org", "medrxiv.org", "arxiv.org")) else 0
    return base_timeout + bonus + (attempt * timeout_step)


def detect_paywall(markdown: str) -> tuple[bool, str | None]:
    lowered = markdown.lower()
    for marker, signal in PAYWALL_MARKERS:
        if marker in lowered:
            return True, signal
    return False, None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"error": "usage: _scrape_markdown.py <url>"}))
        return 1

    url = argv[1]
    token = os.environ.get("FIRECRAWL_KEY") or os.environ.get("FIRECRAWL_API_KEY")
    if not token:
        print(json.dumps({"error": "FIRECRAWL_KEY or FIRECRAWL_API_KEY is required"}))
        return 1

    last_error = None
    max_attempts = env_int("FIRECRAWL_SCRAPE_ATTEMPTS", 4, 1)
    for attempt in range(max_attempts):
        timeout_ms = scrape_timeout_ms(url, attempt)
        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
            "timeout": timeout_ms,
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
                if attempt == max_attempts - 1:
                    break
                time.sleep(2 ** attempt)
                continue
            markdown = data.get("data", {}).get("markdown", "")
            paywall_detected, paywall_signal = detect_paywall(markdown)
            print(json.dumps({
                "success": bool(data.get("success")),
                "markdown": markdown,
                "word_count": len(markdown.split()),
                "content_hash": hash_markdown(markdown),
                "paywall_detected": paywall_detected,
                "paywall_signal": paywall_signal,
                "firecrawl_timeout_ms": timeout_ms,
            }))
            return 0
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            last_error = f"HTTP {exc.code}: {body or exc.reason}"
            if exc.code not in RETRYABLE_HTTP_CODES or attempt == max_attempts - 1:
                break
            time.sleep(2 ** attempt)
        except Exception as exc:
            last_error = str(exc)
            if attempt == max_attempts - 1:
                break
            time.sleep(2 ** attempt)

    print(json.dumps({
        "error": last_error or "Unknown Firecrawl scrape failure",
        "success": False,
        "markdown": "",
        "word_count": 0,
        "content_hash": None,
        "paywall_detected": False,
        "paywall_signal": None,
    }))
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))