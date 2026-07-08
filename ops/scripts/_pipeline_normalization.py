#!/usr/bin/env python3
"""Shared normalization helpers for the Koji ingestion pipeline."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_QUERY_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "source",
}

ENTITY_SUFFIX_PATTERNS = (
    r",?\s*inc\.?$",
    r",?\s*corp\.?$",
    r",?\s*corporation$",
    r",?\s*ltd\.?$",
    r",?\s*limited$",
    r",?\s*llc\.?$",
    r",?\s*plc\.?$",
    r",?\s*company$",
    r",?\s*co\.?$",
    r",?\s*incorporated$",
    r",?\s*ag$",
    r",?\s*sa$",
    r",?\s*gmbh$",
    r",?\s*kk$",
)


def normalize_url(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return ""

    parsed = urlsplit(raw)
    if not parsed.scheme or not parsed.netloc:
        return raw

    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    port = parsed.port
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    else:
        netloc = host

    path = parsed.path or "/"
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    filtered_pairs = [(key, value) for key, value in query_pairs if key.lower() not in TRACKING_QUERY_PARAMS]
    query = urlencode(filtered_pairs, doseq=True)

    return urlunsplit((scheme, netloc, path, query, ""))


def normalize_markdown_for_hash(markdown: str) -> str:
    normalized = unicodedata.normalize("NFC", markdown or "")
    normalized = re.sub(r"<!--.*?-->", "", normalized, flags=re.DOTALL)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\r\n?", "\n", normalized)
    normalized = "\n".join(line.strip() for line in normalized.split("\n"))
    return normalized.strip().lower()


def hash_markdown(markdown: str) -> str:
    return hashlib.sha256(normalize_markdown_for_hash(markdown).encode("utf-8")).hexdigest()


def canonicalize_entity_name(name: str) -> str:
    normalized = (name or "").strip().lower()
    for pattern in ENTITY_SUFFIX_PATTERNS:
        normalized = re.sub(pattern, "", normalized)
    normalized = normalized.rstrip(".,;: ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized