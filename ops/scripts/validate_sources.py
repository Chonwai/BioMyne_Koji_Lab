#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required to validate source manifests", file=sys.stderr)
    sys.exit(2)

REQUIRED_KEYS = {"name", "url", "domain", "source_type", "enabled", "crawl_frequency"}
ALLOWED_DISCOVERY_SURFACES = {"map", "rss", "sitemap"}


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

        primary_surface = source.get("primary_discovery_surface")
        if primary_surface is not None and primary_surface not in ALLOWED_DISCOVERY_SURFACES:
            errors.append(f"source #{idx} invalid primary_discovery_surface: {primary_surface}")

        fallback_surface = source.get("fallback_discovery_surface")
        if fallback_surface is not None and fallback_surface not in ALLOWED_DISCOVERY_SURFACES:
            errors.append(f"source #{idx} invalid fallback_discovery_surface: {fallback_surface}")

        feed_url = source.get("feed_url")
        if feed_url is not None and (not isinstance(feed_url, str) or not feed_url.startswith(("http://", "https://"))):
            errors.append(f"source #{idx} feed_url must be an absolute http(s) URL")
        if primary_surface == "rss" and not feed_url:
            errors.append(f"source #{idx} rss primary_discovery_surface requires feed_url")

        sitemap_urls = source.get("sitemap_urls")
        if sitemap_urls is not None:
            if not isinstance(sitemap_urls, list) or not all(isinstance(item, str) and item.startswith(("http://", "https://")) for item in sitemap_urls):
                errors.append(f"source #{idx} sitemap_urls must be a list of absolute http(s) URLs")

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
