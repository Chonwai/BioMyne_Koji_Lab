#!/usr/bin/env bash
set -euo pipefail

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama is not installed" >&2
  exit 1
fi

MODEL_TAG="${OLLAMA_MODEL_TAG:-}"
if [[ -z "$MODEL_TAG" ]]; then
  echo "OLLAMA_MODEL_TAG is not set; skipping pull" >&2
  exit 1
fi

echo "Pulling model: $MODEL_TAG"
ollama pull "$MODEL_TAG"

echo "Available models:"
curl -s http://localhost:11434/api/tags || true
