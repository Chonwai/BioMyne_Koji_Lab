#!/usr/bin/env python3
"""
BioMyne Koji — Write pipeline output (articles + entities) to Supabase.

Reads a JSONL file where each line is either:
  - A JSON article object (with id, source_id, crawl_run_id, etc.)
  - A line prefixed with 'ENTITY:' followed by a JSON entity-link object

Handles:
  - Article upsert on URL conflict (preserves existing article ID)
  - Entity upsert on (name, entity_type) conflict
  - Article-entity junction inserts
  - Graceful duplicate handling — reports inserted vs duplicate counts

Usage:
  python3 _write_pipeline_output.py <jsonl_file> <source_name>

Environment:
  SUPABASE_URL, SUPABASE_KEY (or SUPABASE_SERVICE_ROLE_KEY)
"""
import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from typing import Optional, Tuple, Union, Dict, List, Any


def supabase_request(method: str, path: str, body: Optional[Dict] = None) -> Tuple[int, Optional[Union[Dict, List]]]:
    """Make a Supabase REST API request. Returns (status_code, response_data)."""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))
    url = f"{supabase_url}{path}"

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }

    data_bytes = None
    if body is not None:
        headers["Prefer"] = "return=representation"
        data_bytes = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_body = resp.read().decode("utf-8")
            status = resp.status
            if resp_body.strip():
                return status, json.loads(resp_body)
            return status, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return e.code, {"error": error_body}
    except Exception as e:
        return 0, {"error": str(e)}


def upsert_article(article: dict) -> tuple[str, str]:
    """
    Upsert an article by URL. Returns (article_db_id, disposition).
    disposition is 'inserted' or 'duplicate'.
    """
    article_id = article.get("id", "")
    url = article.get("url", "")

    # First try to find existing article by URL
    status, existing = supabase_request(
        "GET",
        f"/rest/v1/articles?url=eq.{urllib.parse.quote(url, safe='')}&select=id"
    )

    if status == 200 and isinstance(existing, list) and len(existing) > 0:
        # Article already exists — return existing ID
        return existing[0]["id"], "duplicate"

    # Insert new article (without id, let Supabase generate it)
    insert_body = {
        "source_id": article.get("source_id"),
        "crawl_run_id": article.get("crawl_run_id"),
        "url": url,
        "title": article.get("title", "Untitled"),
        "summary": article.get("summary", ""),
        "topic_tags": _normalize_tags(article.get("topic_tags", [])),
        "priority_level": article.get("priority_level", "medium"),
        "status": article.get("status", "analyzed"),
    }

    status, result = supabase_request("POST", "/rest/v1/articles", insert_body)

    if status == 201 and isinstance(result, list) and len(result) > 0:
        return result[0]["id"], "inserted"

    # If POST failed, try one more time with GET (race condition)
    status2, existing2 = supabase_request(
        "GET",
        f"/rest/v1/articles?url=eq.{urllib.parse.quote(url, safe='')}&select=id"
    )
    if status2 == 200 and isinstance(existing2, list) and len(existing2) > 0:
        return existing2[0]["id"], "duplicate"

    raise RuntimeError(f"Failed to insert or find article: url={url}, status={status}, response={result}")


def _normalize_tags(tags) -> list:
    """Normalize topic_tags to a Python list, whether input is JSON string or list."""
    if isinstance(tags, str):
        try:
            return json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            return [tags] if tags else []
    if isinstance(tags, list):
        return tags
    return []


def normalize_analysis_record(record: dict) -> dict:
    """Convert a raw model output object into an article payload for persistence."""
    src_id = os.environ.get("SRC_ID", "")
    run_id = os.environ.get("RUN_ID", "")
    valid_entities = []
    for entity in record.get("entities", []):
        if not isinstance(entity, dict):
            continue
        name = entity.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        valid_entities.append(
            {
                "name": name.strip(),
                "entity_type": entity.get("entity_type", "company") or "company",
            }
        )
    return {
        "id": str(uuid.uuid4()),
        "source_id": src_id,
        "crawl_run_id": run_id,
        "title": record.get("title", "Untitled"),
        "url": record.get("url", ""),
        "summary": record.get("summary", ""),
        "topic_tags": record.get("topic_tags", []),
        "priority_level": record.get("priority_level", "medium"),
        "status": "analyzed",
        "entities": valid_entities,
    }


def upsert_entity(name: str, entity_type: str) -> str:
    """Upsert an entity by (name, entity_type). Returns entity DB ID."""
    # Check if exists
    status, existing = supabase_request(
        "GET",
        f"/rest/v1/entities?name=eq.{urllib.parse.quote(name, safe='')}&entity_type=eq.{urllib.parse.quote(entity_type, safe='')}&select=id"
    )

    if status == 200 and isinstance(existing, list) and len(existing) > 0:
        return existing[0]["id"]

    # Insert
    status, result = supabase_request("POST", "/rest/v1/entities", {
        "name": name,
        "entity_type": entity_type,
    })

    if status == 201 and isinstance(result, list) and len(result) > 0:
        return result[0]["id"]

    # Retry GET one more time (race condition)
    status2, existing2 = supabase_request(
        "GET",
        f"/rest/v1/entities?name=eq.{urllib.parse.quote(name, safe='')}&entity_type=eq.{urllib.parse.quote(entity_type, safe='')}&select=id"
    )
    if status2 == 200 and isinstance(existing2, list) and len(existing2) > 0:
        return existing2[0]["id"]

    raise RuntimeError(f"Failed to upsert entity: name={name}, type={entity_type}, status={status}")


def link_article_entity(article_id: str, entity_id: str, role: str = "mentioned", mention_count: int = 1) -> bool:
    """Insert an article_entities junction row. Returns True on success."""
    status, result = supabase_request("POST", "/rest/v1/article_entities", {
        "article_id": article_id,
        "entity_id": entity_id,
        "role_in_article": role,
        "mention_count": mention_count,
    })

    if status == 201:
        return True

    # 409 Conflict = junction already exists, that's fine
    if status == 409:
        return True

    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 _write_pipeline_output.py <jsonl_file> [source_name]", file=sys.stderr)
        sys.exit(1)

    jsonl_file = sys.argv[1]
    source_name = sys.argv[2] if len(sys.argv) > 2 else "unknown"

    if not os.path.exists(jsonl_file):
        print(f"JSONL file not found: {jsonl_file}", file=sys.stderr)
        sys.exit(1)

    # Read and parse JSONL. Supports two input shapes:
    # 1. legacy write payload JSONL with ENTITY: lines
    # 2. raw article analysis JSONL (one JSON article object per line)
    articles = []  # list of article dicts
    entities = []  # list of (article_index, entity_dict)
    article_index = -1

    with open(jsonl_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("ENTITY:"):
                entity_data = json.loads(line[7:])
                entities.append((article_index, entity_data))
            else:
                record = json.loads(line)
                if "source_id" in record and "crawl_run_id" in record:
                    articles.append(record)
                else:
                    normalized = normalize_analysis_record(record)
                    articles.append(normalized)
                    for entity in normalized.get("entities", []):
                        entities.append(
                            (
                                article_index + 1,
                                {
                                    "name": entity.get("name", ""),
                                    "entity_type": entity.get("entity_type", "company"),
                                    "role_in_article": "mentioned",
                                    "mention_count": 1,
                                },
                            )
                        )
                article_index += 1

    # Process articles
    article_db_ids = {}  # article_index -> real_db_id
    inserted = 0
    duplicates = 0
    article_errors = 0

    for i, article in enumerate(articles):
        try:
            db_id, disposition = upsert_article(article)
            article_db_ids[i] = db_id
            if disposition == "inserted":
                inserted += 1
            else:
                duplicates += 1
        except Exception as e:
            print(f"  ✗ Article error [{source_name}]: {e}", file=sys.stderr)
            article_errors += 1

    # Process entity links
    entity_success = 0
    entity_errors = 0

    for article_idx, entity_data in entities:
        if article_idx not in article_db_ids:
            # Article failed to insert — skip entity
            entity_errors += 1
            continue

        article_id = article_db_ids[article_idx]
        entity_name = entity_data.get("name", "")
        entity_type = entity_data.get("entity_type", "company")

        if not entity_name:
            entity_errors += 1
            continue

        try:
            entity_db_id = upsert_entity(entity_name, entity_type)
            if link_article_entity(article_id, entity_db_id):
                entity_success += 1
            else:
                entity_errors += 1
        except Exception as e:
            print(f"  ✗ Entity error [{source_name}]: {e}", file=sys.stderr)
            entity_errors += 1

    # Output summary as JSON (for the bash pipeline to parse)
    summary = {
        "source": source_name,
        "articles_inserted": inserted,
        "articles_duplicate": duplicates,
        "articles_errors": article_errors,
        "entity_links_success": entity_success,
        "entity_links_errors": entity_errors,
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
