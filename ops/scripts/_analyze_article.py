#!/usr/bin/env python3
"""Analyze a single scraped article with the local LLM via Hermes."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request

try:
    from _pipeline_normalization import hash_markdown
except ModuleNotFoundError:
    from ops.scripts._pipeline_normalization import hash_markdown


ALLOWED_ENTITY_TYPES = {"company", "drug", "person", "technology", "deal"}


def sentence_count(text: str) -> int:
    parts = [part.strip() for part in re.split(r"[.!?。！？]+", text) if part.strip()]
    return len(parts)


def summary_needs_expansion(summary: str, min_chars: int, min_sentences: int) -> bool:
    cleaned = summary.strip()
    if not cleaned:
        return True
    if len(cleaned) < min_chars:
        return True
    return sentence_count(cleaned) < min_sentences


def build_prompt(
    source_name: str,
    source_url: str,
    article_url: str,
    title_hint: str,
    markdown: str,
    require_expanded_summary: bool,
) -> str:
    summary_instruction = (
        "4-6 sentence executive summary covering who/what happened, the concrete evidence or result, "
        "and why the article matters for biotech operators or investors."
    )
    retry_note = ""
    if require_expanded_summary:
        retry_note = (
            "\n- The previous summary was too short. Expand it materially and include enough factual detail "
            "that an executive can understand the article without opening the raw markdown."
        )

    return f'''You are a biotech intelligence analyst. Analyze this single article from {source_name} ({source_url}).

Return exactly one JSON object and nothing else using this schema:

{{
  "title": "Article headline",
  "url": "{article_url}",
  "summary": "{summary_instruction}",
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
- The summary must be a dense executive summary, not a headline rewrite.
- Mention named companies, drugs, trials, approvals, deals, or scientific outcomes when present.
- If the content is weak or not actually an article, still return valid JSON with low priority and explain uncertainty in analysis_notes.
- Do not wrap the JSON in markdown fences.{retry_note}

ARTICLE MARKDOWN:
{markdown}
'''


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
    summary_min_chars = int(os.environ.get("SUMMARY_MIN_CHARS", "220"))
    summary_min_sentences = int(os.environ.get("SUMMARY_MIN_SENTENCES", "4"))
    article_published_at = os.environ.get("ARTICLE_PUBLISHED_AT", "").strip()
    discovery_method = os.environ.get("DISCOVERY_METHOD", "map").strip() or "map"
    analysis_version = os.environ.get("ANALYSIS_PROMPT_VERSION", "biotech-article-analysis-v2")
    existing_article_id = os.environ.get("EXISTING_ARTICLE_ID", "").strip() or None
    processing_lane = os.environ.get("PROCESSING_LANE", "new").strip() or "new"

    with open(markdown_file, "r", encoding="utf-8") as f:
        markdown = f.read()

    last_error = None
    article = None
    require_expanded_summary = False
    for attempt in range(2):
        payload = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": build_prompt(
                    source_name,
                    source_url,
                    article_url,
                    title_hint,
                    markdown,
                    require_expanded_summary,
                ),
            }],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }
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

            if not require_expanded_summary and summary_needs_expansion(
                str(article.get("summary", "")),
                summary_min_chars,
                summary_min_sentences,
            ):
                require_expanded_summary = True
                article = None
                last_error = "summary too short"
                time.sleep(1)
                continue
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
    article["raw_markdown"] = markdown
    article["published_at"] = article_published_at or None
    article["discovery_method"] = discovery_method
    article["existing_article_id"] = existing_article_id
    article["processing_lane"] = processing_lane
    article["skip_analysis"] = False
    article["content_unchanged"] = False
    article["content_hash"] = hash_markdown(markdown)
    article["analysis_version"] = analysis_version
    article["analysis_fingerprint"] = {
        "prompt_template_version": analysis_version,
        "model": model,
        "temperature": 0.3,
        "content_hash": article["content_hash"],
        "analysis_type": "summary+tags+entities",
    }

    print(json.dumps(article))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))