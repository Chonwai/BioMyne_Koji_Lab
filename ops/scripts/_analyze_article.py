#!/usr/bin/env python3
"""Analyze a single scraped article with the local LLM via Hermes."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request


ALLOWED_ENTITY_TYPES = {"company", "drug", "person", "technology", "deal"}


def sanitize_entities(raw_entities: object) -> list[dict]:
    cleaned = []
    if not isinstance(raw_entities, list):
        return cleaned
    for entity in raw_entities:
        if not isinstance(entity, dict):
            continue
        name = entity.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        entity_type = entity.get("entity_type", "company")
        if entity_type not in ALLOWED_ENTITY_TYPES:
            entity_type = "company"
        cleaned.append({"name": name.strip(), "entity_type": entity_type})
    return cleaned


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"error": "usage: _analyze_article.py <markdown_file>"}))
        return 1

    markdown_file = argv[1]
    source_name = os.environ.get("SRC_NAME", "")
    source_url = os.environ.get("SRC_URL", "")
    article_url = os.environ.get("ARTICLE_URL", source_url)
    title_hint = os.environ.get("TITLE_HINT", "")
    model = os.environ.get("MODEL", os.environ.get("OLLAMA_MODEL_TAG", "qwen3.6:35b-mlx"))
    hermes_url = os.environ.get("HERMES_URL", "http://localhost:8642")
    hermes_key = os.environ.get("HERMES_KEY", "koji-phase1-local")
    max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "4096"))
    timeout = int(os.environ.get("LLM_TIMEOUT", "180"))

    with open(markdown_file, "r", encoding="utf-8") as f:
        markdown = f.read()

    prompt = f'''You are a biotech intelligence analyst. Analyze this single article from {source_name} ({source_url}).

Return exactly one JSON object and nothing else using this schema:

{{
  "title": "Article headline",
  "url": "{article_url}",
  "summary": "2-3 sentence summary of key findings",
  "topic_tags": ["tag1", "tag2"],
  "priority_level": "high|medium|low",
  "entities": [
    {{"name": "Company or drug name", "entity_type": "company|drug|person|technology|deal"}}
  ],
  "analysis_notes": "Optional note when content quality is weak"
}}

Rules:
- Use the article URL provided above for the url field.
- Prefer the article's own title; title hint: {title_hint or 'N/A'}.
- If the content is weak or not actually an article, still return valid JSON with low priority and explain uncertainty in analysis_notes.
- Do not wrap the JSON in markdown fences.

ARTICLE MARKDOWN:
{markdown}
'''

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    last_error = None
    article = None
    for attempt in range(2):
        req = urllib.request.Request(
            f"{hermes_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {hermes_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                response_data = json.loads(resp.read())

            content = response_data["choices"][0]["message"]["content"]
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in model response")

            article = json.loads(match.group())
            if not isinstance(article, dict):
                raise ValueError("Model response did not parse to a JSON object")
            break
        except Exception as exc:
            last_error = str(exc)
            article = None
            if attempt == 1:
                print(json.dumps({"error": last_error}))
                return 1
            time.sleep(1)

    if article is None:
        print(json.dumps({"error": last_error or "Unknown article analysis failure"}))
        return 1

    article.setdefault("title", title_hint or "Untitled")
    article["url"] = article_url
    article.setdefault("summary", "")
    article.setdefault("topic_tags", [])
    article.setdefault("priority_level", "low")
    article["entities"] = sanitize_entities(article.get("entities", []))
    article.setdefault("analysis_notes", "")

    print(json.dumps(article))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))