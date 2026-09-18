#!/usr/bin/env python3
"""Scrape a single URL via the configured provider (local or firecrawl_cloud).

Usage: _scrape_via_provider.py <url> [provider]
Output: JSON identical to _scrape_markdown.py (for drop-in replacement in run_pipeline.sh).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

# Ensure ops/scripts is on path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler_providers import create_provider


async def _main(url: str, provider_name: str | None) -> int:
    provider = create_provider(provider_name)
    result = await provider.scrape(url)

    # Convert dataclass to dict, handle None values
    output: dict = {
        "success": result.success,
        "markdown": result.markdown or "",
        "word_count": result.word_count,
        "content_hash": result.content_hash or "",
        "paywall_detected": result.paywall_detected,
        "paywall_signal": result.paywall_signal,
        "provider": result.provider,
    }
    if result.firecrawl_timeout_ms is not None:
        output["firecrawl_timeout_ms"] = result.firecrawl_timeout_ms
    if result.error:
        output["error"] = result.error

    print(json.dumps(output))
    return 0 if result.success else 1


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: _scrape_via_provider.py <url> [provider]"}))
        return 1

    url = sys.argv[1]
    provider_name = sys.argv[2] if len(sys.argv) > 2 else None
    return asyncio.run(_main(url, provider_name))


if __name__ == "__main__":
    raise SystemExit(main())
