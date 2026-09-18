#!/usr/bin/env python3
"""Thin CLI wrapper over FirecrawlProvider (migration spec §5 / Step 3).

Scrape logic (Firecrawl /v1/scrape, retries, paywall detection) lives in
`crawler_providers.FirecrawlProvider`; this module stays a stable entry point
(CLI + importable symbols) for existing callers such as run_pipeline.sh and
ops/tests.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import sys

try:
    from crawler_providers import FirecrawlProvider, PAYWALL_MARKERS, detect_paywall
except ModuleNotFoundError:
    from ops.scripts.crawler_providers import FirecrawlProvider, PAYWALL_MARKERS, detect_paywall

__all__ = ["PAYWALL_MARKERS", "detect_paywall", "main"]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"error": "usage: _scrape_markdown.py <url>"}))
        return 1

    result = asyncio.run(FirecrawlProvider().scrape(argv[1]))
    print(json.dumps(dataclasses.asdict(result)))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))