#!/usr/bin/env python3
"""Emit a minimal Langfuse v2 trace for a manual Koji pipeline run."""

import json
import os
import sys


def main() -> int:
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")
    host = os.environ.get("LANGFUSE_BASE_URL", "http://localhost:3001")

    if not public_key or not secret_key:
        print(json.dumps({"status": "skipped", "reason": "missing_langfuse_keys"}))
        return 0

    try:
        from langfuse import Langfuse
    except ImportError:
        print(json.dumps({"status": "skipped", "reason": "langfuse_sdk_not_installed"}))
        return 0

    payload = json.load(sys.stdin)

    langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)

    output = {
        "status": payload.get("status", "unknown"),
        "source_count": payload.get("source_count", 0),
        "article_count": payload.get("article_count", 0),
        "error_count": payload.get("error_count", 0),
        "scraped_dir": payload.get("scraped_dir", ""),
    }

    trace = langfuse.trace(
        name="koji-manual-pipeline-run",
        input={
            "run_id": payload.get("run_id", ""),
            "trigger": payload.get("trigger", "manual"),
            "model": payload.get("model", ""),
        },
        output=output,
        tags=["koji", "phase1", "manual-run"],
        metadata={
            "repo": "biomyne-koji",
            "raw_data_dir": payload.get("scraped_dir", ""),
        },
    )
    span = trace.span(
        name="koji_manual_pipeline",
        input={
            "run_id": payload.get("run_id", ""),
            "trigger": payload.get("trigger", "manual"),
            "model": payload.get("model", ""),
        },
        metadata={
            "pipeline": "BioMyne Koji",
            "delivery_channel": payload.get("delivery_channel", "manual"),
            "source_count": payload.get("source_count", 0),
        },
    )
    span.end(
        output=output,
        level="ERROR" if payload.get("error_count", 0) else "DEFAULT",
        status_message=(
            "pipeline completed with errors"
            if payload.get("error_count", 0)
            else "pipeline completed successfully"
        ),
        metadata={
            "model": payload.get("model", ""),
            "usage_details": {
                "sources": payload.get("source_count", 0),
                "articles": payload.get("article_count", 0),
            },
        },
    )
    langfuse.flush()

    print(
        json.dumps(
            {
                "status": "ok",
                "trace_id": trace.id,
                "trace_url": trace.get_trace_url(),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())