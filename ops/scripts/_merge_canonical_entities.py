#!/usr/bin/env python3
"""Merge duplicate entities that share the same canonical_name + entity_type."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def supabase_request(method: str, path: str, body: Optional[dict] = None) -> Tuple[int, object]:
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))
    if not supabase_url or not supabase_key:
        return 0, {"error": "supabase_not_configured"}

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }

    data_bytes = None
    if body is not None:
        headers["Prefer"] = "return=representation"
        data_bytes = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        f"{supabase_url}{path}",
        data=data_bytes,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read().decode("utf-8")
            return resp.status, json.loads(payload) if payload.strip() else None
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore") if exc.fp else exc.reason
        return exc.code, {"error": body_text}
    except Exception as exc:
        return 0, {"error": str(exc)}


def fetch_entities() -> List[dict]:
    status, payload = supabase_request(
        "GET",
        "/rest/v1/entities?select=id,name,canonical_name,entity_type,created_at&canonical_name=not.is.null&order=created_at.asc",
    )
    if status == 200 and isinstance(payload, list):
        return payload
    raise RuntimeError(f"Failed to fetch entities: status={status}, payload={payload}")


def fetch_article_links(entity_id: str) -> List[dict]:
    status, payload = supabase_request(
        "GET",
        f"/rest/v1/article_entities?entity_id=eq.{urllib.parse.quote(entity_id, safe='')}&select=id,article_id,role_in_article,mention_count",
    )
    if status == 200 and isinstance(payload, list):
        return payload
    raise RuntimeError(f"Failed to fetch article links for entity {entity_id}: status={status}, payload={payload}")


def find_existing_master_link(article_id: str, entity_id: str) -> Optional[dict]:
    status, payload = supabase_request(
        "GET",
        f"/rest/v1/article_entities?article_id=eq.{urllib.parse.quote(article_id, safe='')}&entity_id=eq.{urllib.parse.quote(entity_id, safe='')}&select=id,mention_count&limit=1",
    )
    if status == 200 and isinstance(payload, list) and payload:
        return payload[0]
    return None


def patch_article_link(link_id: str, mention_count: int) -> None:
    status, payload = supabase_request(
        "PATCH",
        f"/rest/v1/article_entities?id=eq.{urllib.parse.quote(link_id, safe='')}",
        {"mention_count": mention_count},
    )
    if status not in (200, 204):
        raise RuntimeError(f"Failed to patch article_entities {link_id}: status={status}, payload={payload}")


def insert_article_link(article_id: str, entity_id: str, role_in_article: str, mention_count: int) -> None:
    status, payload = supabase_request(
        "POST",
        "/rest/v1/article_entities",
        {
            "article_id": article_id,
            "entity_id": entity_id,
            "role_in_article": role_in_article,
            "mention_count": mention_count,
        },
    )
    if status not in (200, 201):
        raise RuntimeError(
            f"Failed to insert article_entities link article={article_id} entity={entity_id}: status={status}, payload={payload}"
        )


def delete_by_filter(path: str) -> None:
    status, payload = supabase_request("DELETE", path)
    if status not in (200, 204):
        raise RuntimeError(f"Failed delete for {path}: status={status}, payload={payload}")


def choose_master(group: List[dict]) -> dict:
    return sorted(group, key=lambda item: (item.get("created_at") or "", item.get("id") or ""))[0]


def main(argv: List[str]) -> int:
    apply_changes = "--apply" in argv[1:]
    entities = fetch_entities()

    grouped: Dict[tuple[str, str], List[dict]] = defaultdict(list)
    for entity in entities:
        key = (str(entity.get("canonical_name") or "").strip(), str(entity.get("entity_type") or "").strip())
        if not key[0] or not key[1]:
            continue
        grouped[key].append(entity)

    duplicate_groups = {key: group for key, group in grouped.items() if len(group) > 1}
    summary = {
        "mode": "apply" if apply_changes else "dry_run",
        "groups_found": len(duplicate_groups),
        "entities_to_merge": 0,
        "article_links_reassigned": 0,
        "article_links_merged": 0,
        "entities_deleted": 0,
        "groups": [],
    }

    for (canonical_name, entity_type), group in sorted(duplicate_groups.items()):
        master = choose_master(group)
        duplicates = [item for item in group if item["id"] != master["id"]]
        summary["entities_to_merge"] += len(duplicates)

        group_report = {
            "canonical_name": canonical_name,
            "entity_type": entity_type,
            "master_id": master["id"],
            "duplicate_ids": [item["id"] for item in duplicates],
        }
        summary["groups"].append(group_report)

        if not apply_changes:
            continue

        for duplicate in duplicates:
            duplicate_links = fetch_article_links(duplicate["id"])
            for link in duplicate_links:
                existing_master_link = find_existing_master_link(link["article_id"], master["id"])
                if existing_master_link:
                    merged_count = int(existing_master_link.get("mention_count") or 0) + int(link.get("mention_count") or 0)
                    patch_article_link(existing_master_link["id"], merged_count)
                    summary["article_links_merged"] += 1
                else:
                    insert_article_link(
                        link["article_id"],
                        master["id"],
                        str(link.get("role_in_article") or "mentioned"),
                        int(link.get("mention_count") or 1),
                    )
                    summary["article_links_reassigned"] += 1

            delete_by_filter(f"/rest/v1/article_entities?entity_id=eq.{urllib.parse.quote(duplicate['id'], safe='')}")
            delete_by_filter(f"/rest/v1/entities?id=eq.{urllib.parse.quote(duplicate['id'], safe='')}")
            summary["entities_deleted"] += 1

    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))