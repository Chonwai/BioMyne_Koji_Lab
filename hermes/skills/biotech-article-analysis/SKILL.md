# biotech-article-analysis

## Purpose

Analyze crawled biotech article content and emit structured JSON.

## Inputs

- `article_url`
- `source_name`
- `published_at`
- `raw_markdown`

## Outputs

- `title`
- `summary`
- `priority_level`
- `topic_tags`
- `entities`
- `analysis_notes`

## Procedure

1. Read the article markdown.
2. Apply the approved Phase 1 prompt template.
3. Return valid JSON only.
4. Mark uncertainty in `analysis_notes` if content quality is weak.

## Failure Rules

- malformed JSON => mark as `JSON_MALFORMED`
- missing required keys => mark article `needs_review`
