#!/usr/bin/env python3
"""
BioMyne Koji — Build LLM chat completion request JSON.

Reads the analysis prompt from stdin, reads MODEL from OLLAMA_MODEL_TAG
environment variable, and outputs the JSON request body for a Hermes
/v1/chat/completions call.

Usage:
  echo "$PROMPT" | python3 _build_llm_request.py
"""
import json
import os
import sys


def main() -> None:
    prompt = sys.stdin.read()
    model = os.environ.get("OLLAMA_MODEL_TAG", "qwen3.6:35b-mlx")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
        "temperature": 0.3,
    }

    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
