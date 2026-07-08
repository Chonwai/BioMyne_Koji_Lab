#!/usr/bin/env python3
"""Scrape a single page to markdown via Firecrawl /v1/scrape with retries."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"error": "usage: _scrape_markdown.py <url>"}))
        return 1

    url = argv[1]
    token = os.environ.get("FIRECRAWL_KEY") or os.environ.get("FIRECRAWL_API_KEY")
    if not token:
        print(json.dumps({"error": "FIRECRAWL_KEY or FIRECRAWL_API_KEY is required"}))
        return 1

    payload = {
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True,
    }

    last_error = None
    for attempt in range(3):
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
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            markdown = data.get("data", {}).get("markdown", "")
            print(json.dumps({"success": bool(data.get("success")), "markdown": markdown, "word_count": len(markdown.split())}))
            return 0
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            last_error = f"HTTP {exc.code}: {body or exc.reason}"
            if exc.code not in (408, 409, 425, 429, 500, 502, 503, 504) or attempt == 2:
                break
            time.sleep(2 ** attempt)
        except Exception as exc:
            last_error = str(exc)
            if attempt == 2:
                break
            time.sleep(2 ** attempt)

    print(json.dumps({"error": last_error or "Unknown Firecrawl scrape failure", "success": False, "markdown": "", "word_count": 0}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))