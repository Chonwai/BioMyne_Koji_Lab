#!/usr/bin/env python3
"""Fetch Firecrawl cloud credit usage for observability."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    token = os.environ.get("FIRECRAWL_KEY") or os.environ.get("FIRECRAWL_API_KEY")
    if not token:
        print(json.dumps({"error": "FIRECRAWL_KEY or FIRECRAWL_API_KEY is required"}))
        return 1

    req = urllib.request.Request(
        "https://api.firecrawl.dev/v1/team/credit-usage",
        headers={
            "Authorization": f"Bearer {token}",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else exc.reason
        print(json.dumps({"error": f"HTTP {exc.code}: {body}"}))
        return 1
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    print(
        json.dumps(
            {
                "remaining_credits": data.get("remaining_credits"),
                "plan_credits": data.get("plan_credits"),
                "billing_period_start": data.get("billing_period_start"),
                "billing_period_end": data.get("billing_period_end"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())