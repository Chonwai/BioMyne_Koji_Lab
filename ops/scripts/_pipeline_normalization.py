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


# ── Boilerplate exclusion patterns (P2 F-2) ────────────────────────────────
# Line-level filters applied BEFORE the legacy 6-step char-level normalization.
# Each targets a known dynamic page element that is:
#   (a) irrelevant to content identity (cookie consent / ads / session tokens)
#   (b) rendered nondeterministically across requests
# The rules are intentionally conservative (anchored, known boilerplate text)
# to avoid false positives on genuine article prose.

# CSRF-protected link lines, e.g. Nature "Save article" links:
#   [ Save article ](https://www.nature.com/articles/.../save-research?_csrf=...)
# The _csrf token changes on every request (100% drift). Removing the whole
# query keeps the link text so article prose near it is untouched.
CSRF_URL_RE = re.compile(r"(?P<scheme>https?://[^\s)\]]+)_csrf=[^\s)\]]+", re.IGNORECASE)

# OneTrust cookie-consent modal (STAT News / Boston Globe Media). The modal is
# rendered as a markdown block whose extent is variable (observed 30+ lines):
#
#   ![STAT News](https://cdn.cookielaw.org/logos/static/ot_company_logo.png)
#   ## Privacy Preference Center
#   When you visit any website, it may store or retrieve information...
#   [More information](https://cookiepedia.co.uk/giving-consent-to-cookies)
#   Allow All
#   ### Manage Consent Preferences
#   #### Strictly Necessary Cookies / Targeting / Performance / Functional
#   ### Cookie List ... Apply Cancel ... Reject All Confirm My Choices
#   [![Powered by Onetrust](...)](https://www.onetrust.com/products/cookie-consent/)
#
# Nature's cookie banner (observed in fit_markdown, ~7 lines, randomly kept):
#
#   ## Your privacy, your choice
#   We use essential cookies to make sure the site can function. We also use
#   optional cookies for advertising, personalisation of content, usage
#   analysis, and social media ...
#   By accepting optional cookies, you consent to the processing of your
#   personal data - including transfers to third parties. Some third parties
#   are outside of the European Economic Area, with varying standards of data
#   protection.
#   See our [privacy policy](https://www.nature.com/info/privacy) for more
#   information on the use of your personal data.
#   Manage preferences for further information and to change your choices.
#   Accept all cookies Reject optional cookies
#
# Strategy: block removal from the first START marker line through the
# terminal END marker line ("Confirm My Choices" button / Onetrust footer /
# "Accept all cookies" line). START markers are banner-unique strings
# (headers, consent text); END markers are the terminal button / footer.
# In normal mode, lines that match an END marker are also dropped outright
# (they are pure boilerplate and never article prose).
COOKIE_MODAL_START_RE = re.compile(
    r"cdn\.cookielaw\.org|"
    r"(?:##\s*)?Privacy Preference Center\b|"
    r"cookiepedia\.co\.uk/giving-consent-to-cookies|"
    r"(?:##\s*)?Your privacy, your choice\b|"
    r"nature\.com/info/privacy|"
    r"By clicking .?Accept Non-Essential Cookies",
    re.IGNORECASE,
)
COOKIE_MODAL_END_RE = re.compile(
    r"Confirm My Choices\s*$|"
    r"\[!\[Powered by Onetrust|"
    r"onetrust\.com/products/cookie-consent|"
    r"Accept all cookies|"
    r"Reject optional cookies|"
    r"(?:Reject|Accept) Non-Essential Cookies",
    re.IGNORECASE,
)

# Inline ad-slot lines (GEN): sometimes present, sometimes not.
ADVERTISEMENT_LINE_RE = re.compile(r"^\s*(?:ADVERTISEMENT|Advertisement)\s*$")
SCROLL_TO_CONTINUE_LINE_RE = re.compile(r"^\s*SCROLL TO CONTINUE(?: WITH CONTENT)?\s*$")

# Safety cap: if the modal is truncated (no END marker found), stop dropping
# lines after this many so we never swallow real article prose. Observed modal
# is ~33 lines; 60 leaves generous headroom while bounding worst-case loss.
MAX_COOKIE_MODAL_LINES = 60


def _is_cookie_modal_line(line: str) -> bool:
    """True if a line marks the START of the OneTrust cookie-consent modal."""
    return bool(COOKIE_MODAL_START_RE.search(line))


def _is_cookie_modal_end_line(line: str) -> bool:
    """True if a line closes the cookie modal block (Apply/Cancel/Reject/Powered by)."""
    return bool(COOKIE_MODAL_END_RE.search(line))


def exclude_boilerplate_lines(lines: list[str]) -> list[str]:
    """Drop lines belonging to known non-content boilerplate.

    Applies three conservative, anchored filters:
      1. _csrf URL query parameter (Nature) -- handled earlier as a regex sub
      2. OneTrust cookie-consent modal block (STAT): block removal from the
         first START marker through the terminal END marker; standalone
         END-marker lines are dropped in normal mode too.
      3. ADVERTISEMENT / SCROLL TO CONTINUE ad-slot lines (GEN)
    """
    filtered: list[str] = []
    in_cookie_modal = False
    modal_lines = 0
    for line in lines:
        if in_cookie_modal:
            modal_lines += 1
            if _is_cookie_modal_end_line(line):
                in_cookie_modal = False
            elif modal_lines > MAX_COOKIE_MODAL_LINES:
                # Truncated modal (no END marker within cap): stop dropping.
                in_cookie_modal = False
                filtered.append(line)
            continue
        if _is_cookie_modal_line(line):
            # START marker takes precedence over END: a line like
            # 'By clicking "Accept Non-Essential Cookies"...' is the banner
            # OPENING, not a standalone closing line, even though it contains
            # the END substring. Enter modal mode and drop it.
            in_cookie_modal = True
            modal_lines = 1
            continue
        if _is_cookie_modal_end_line(line):
            # Standalone footer/button line (modal already ended): drop.
            continue
        if ADVERTISEMENT_LINE_RE.match(line) or SCROLL_TO_CONTINUE_LINE_RE.match(line):
            continue
        filtered.append(line)
    return filtered


def normalize_markdown_for_hash(markdown: str) -> str:
    """Canonical normalization for content-identity hashing.

    Order of operations:
      1. Line-level boilerplate exclusion (P2 F-2):
         - _csrf URL query params
         - OneTrust cookie-consent modal block
         - ADVERTISEMENT / SCROLL TO CONTINUE ad-slot lines
      2. Legacy 6-step char-level normalization (unchanged):
         NFC -> strip HTML comments -> collapse whitespace -> CRLF->LF ->
         strip each line -> strip + lowercase.
    """
    # Pre-filter: CSRF query params anywhere (URLs may contain the token in
    # the middle of a line; do this before line-splitting).
    cleaned = CSRF_URL_RE.sub(r"\g<scheme>", markdown or "")

    # Line-level boilerplate exclusion.
    lines = cleaned.split("\n")
    filtered_lines = exclude_boilerplate_lines(lines)

    # Legacy 6-step char-level normalization (kept byte-for-byte).
    normalized = unicodedata.normalize("NFC", "\n".join(filtered_lines))
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