#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required to validate source manifests", file=sys.stderr)
    sys.exit(2)

REQUIRED_KEYS = {"name", "url", "domain", "source_type", "enabled", "crawl_frequency"}


def main(path_str: str) -> int:
    path = Path(path_str)
    if not path.exists():
        print(f"Manifest not found: {path}", file=sys.stderr)
        return 1

    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or "sources" not in data or not isinstance(data["sources"], list):
        print("Manifest must contain a top-level 'sources' list", file=sys.stderr)
        return 1

    urls = set()
    errors = []
    for idx, source in enumerate(data["sources"], start=1):
        if not isinstance(source, dict):
            errors.append(f"source #{idx} must be an object")
            continue
        missing = REQUIRED_KEYS - set(source.keys())
        if missing:
            errors.append(f"source #{idx} missing keys: {sorted(missing)}")
        url = source.get("url")
        if url in urls:
            errors.append(f"duplicate url: {url}")
        urls.add(url)

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    print(f"Manifest valid: {len(data['sources'])} sources")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_sources.py <manifest_path>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
