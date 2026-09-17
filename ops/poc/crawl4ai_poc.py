#!/usr/bin/env python3
"""Crawl4AI PoC — evaluate local Playwright + Crawl4AI as a Firecrawl replacement.

⚠️ STANDALONE PoC — does NOT touch the Koji pipeline (run_pipeline.py,
_scrape_markdown.py, _discover_article_urls.py, .env, sql/ are all untouched).

Requirements (NOT installed by this script — install manually if you want to run):
    pip install crawl4ai playwright
    playwright install chromium

Usage:
    python3 ops/poc/crawl4ai_poc.py --url https://www.biorxiv.org/content/10.1101/2026.01.01.123456
    python3 ops/poc/crawl4ai_poc.py --url https://www.statnews.com/2026/09/01/example/ --llm
    python3 ops/poc/crawl4ai_poc.py --stdin            # read URLs from stdin, one per line

Behavior:
    * AsyncWebCrawler fetches a public article page (bioRxiv / STAT News — no paywall).
    * Extracts markdown (Crawl4AI's onlyMainContent equivalent).
    * Optionally runs LLMExtractionStrategy with a local Ollama model
      (provider="ollama/qwen3.6:35b-mlx"). If Ollama is unavailable, it degrades
      gracefully to markdown-only output (never crashes the PoC).
    * Prints word count + first 500 chars of markdown + LLM result (when available).

Ollama provider note: Crawl4AI LLMExtractionStrategy accepts
provider="ollama/qwen3.6:35b-mlx" with base_url="http://localhost:11434" and
api_token=None for a local Ollama endpoint.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any

# Public, non-paywalled demo URLs (bioRxiv preprints and STAT News are the pilot pair)
DEFAULT_URLS = [
    "https://www.biorxiv.org/content/10.1101/2024.05.21.595135v1",  # bioRxiv preprint
    "https://www.statnews.com/2024/05/20/vertex-crinetics-acquisition/",  # STAT News (public)
]

# Matches the Koji pipeline's LLM model tag (smoke_test.sh default).
DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL_TAG", "qwen3.6:35b-mlx")

LLM_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "priority_level": {"type": "string", "enum": ["high", "medium", "low"]},
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "entity_type": {"type": "string", "enum": ["company", "drug", "person", "technology", "deal"]},
                },
                "required": ["name", "entity_type"],
            },
        },
    },
    "required": ["title", "summary", "priority_level"],
}


def _check_ollama(url: str, timeout: float = 3.0) -> bool:
    """Cheap probe: is Ollama reachable at the given URL? Never throws."""
    try:
        import urllib.request

        req = urllib.request.Request(url.rstrip("/") + "/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


async def crawl_one(url: str, use_llm: bool, ollama_url: str, model: str) -> dict[str, Any]:
    """Crawl a single URL with Crawl4AI. Returns a dict — never raises on content issues."""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
    except ImportError as exc:
        return {
            "url": url,
            "error": f"crawl4ai not installed: {exc}. Run: pip install crawl4ai playwright && playwright install chromium",
            "success": False,
        }

    browser_cfg = BrowserConfig(
        headless=True,
        # Keep the footprint small for the PoC; production would tune this.
    )

    run_kwargs: dict[str, Any] = {
        "markdown": True,
        "only_main_content": True,
        "cache_mode": CacheMode.BYPASS,
    }

    if use_llm:
        llm = LLMExtractionStrategy(
            provider=f"ollama/{model}",
            schema=LLM_SCHEMA,
            extraction_type="schema",
            instruction=(
                "Extract the article title, a dense executive summary covering who/what "
                "happened and why it matters for biotech operators or investors, a "
                "priority_level (high|medium|low), and named entities (company, drug, "
                "person, technology, deal). Return valid JSON."
            ),
            base_url=ollama_url,
            api_token=None,  # local Ollama: no auth token needed
            verbose=False,
        )
        run_kwargs["extraction_strategy"] = llm

    run_cfg = CrawlerRunConfig(**run_kwargs)

    result: dict[str, Any] = {"url": url, "success": False}

    try:
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            crawl = await crawler.arun(url=url, config=run_cfg)
            result["success"] = bool(getattr(crawl, "success", False))
            result["status_code"] = getattr(crawl, "status_code", None)

            markdown = getattr(crawl, "markdown", "") or ""
            result["markdown"] = markdown
            result["word_count"] = len(markdown.split())
            result["markdown_preview"] = markdown[:500]

            if use_llm:
                extracted = getattr(crawl, "extracted_content", None)
                if extracted:
                    try:
                        result["llm"] = json.loads(extracted)
                    except (TypeError, ValueError):
                        result["llm"] = {"raw": str(extracted)}
                else:
                    result["llm"] = {"error": "no extracted_content returned"}

            if not result["success"]:
                err = getattr(crawl, "error_message", None)
                result["error"] = err or "crawl returned success=False without error message"
    except Exception as exc:  # network / browser failures degrade to a report, not a crash
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


async def main_async(args: argparse.Namespace) -> int:
    ollama_ok = _check_ollama(args.ollama_url)
    if args.use_llm and not ollama_ok:
        print(f"[poc] ⚠️ Ollama not reachable at {args.ollama_url} — degrading to markdown-only "
              f"(graceful degradation).\n", file=sys.stderr)

    exit_code = 0
    for url in args.urls:
        print(f"━━━ Crawling: {url} ━━━")
        result = await crawl_one(url, args.use_llm and ollama_ok, args.ollama_url, args.model)

        if result.get("error"):
            print(f"  ❌ Error: {result['error']}")
            exit_code = 1
            continue

        print(f"  ✅ status={result.get('status_code')} word_count={result.get('word_count')}")
        print(f"  ── markdown (first 500 chars) ──")
        print(f"  {result.get('markdown_preview', '')!r}")
        if "llm" in result:
            print(f"  ── LLM extraction (Ollama {args.model}) ──")
            print(f"  {json.dumps(result['llm'], ensure_ascii=False, indent=2)}")
        print()

        # Clean up the big markdown field before the final JSON report.
        result.pop("markdown", None)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()

    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl4AI PoC — evaluate local Playwright+Crawl4AI as Firecrawl replacement.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 ops/poc/crawl4ai_poc.py --url https://www.biorxiv.org/content/10.1101/2024.05.21.595135v1\n"
            "  python3 ops/poc/crawl4ai_poc.py --llm\n"
            "  echo 'https://example.com/a https://example.com/b' | python3 ops/poc/crawl4ai_poc.py --stdin\n"
        ),
    )
    parser.add_argument("--url", action="append", dest="urls", default=None,
                        help="URL to crawl (repeatable). Defaults to a bioRxiv + STAT News demo pair.")
    parser.add_argument("--stdin", action="store_true",
                        help="Read whitespace-separated URLs from stdin instead of defaults.")
    parser.add_argument("--llm", action="store_true",
                        help="Enable LLMExtractionStrategy via local Ollama (degrades to markdown-only if unreachable).")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL,
                        help=f"Ollama base URL (default: {DEFAULT_OLLAMA_URL})")
    parser.add_argument("--model", default=DEFAULT_OLLAMA_MODEL,
                        help=f"Ollama model tag (default: {DEFAULT_OLLAMA_MODEL})")
    args = parser.parse_args(argv)

    if args.stdin:
        raw = sys.stdin.read().split()
        if not raw:
            print("Error: --stdin given but no URLs provided", file=sys.stderr)
            return 1
        args.urls = raw
    elif not args.urls:
        args.urls = list(DEFAULT_URLS)

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
