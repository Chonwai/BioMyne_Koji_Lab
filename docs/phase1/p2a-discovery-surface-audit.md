# P2A0 Discovery Surface Audit

## Status

| Field | Value |
| --- | --- |
| Status | Completed for all 11 configured sources |
| Date | 2026-07-08 |
| Scope | 5 pilot sources + 6 additional validated sources |
| Purpose | Satisfy P2A0 gate before P2A implementation |

## Pilot Set

| Source | Family | Primary Surface | Fallback Surface | Sample URL / Signal | Known Failure Mode |
| --- | --- | --- | --- | --- | --- |
| STAT News | News | RSS | Map | `https://www.statnews.com/feed/` returns `200` + `application/rss+xml` | Feed temporarily stale or cached behind CDN |
| Fierce Biotech | News | RSS | Map | `https://www.fiercebiotech.com/rss/xml` returns `200` + `application/rss+xml` | Feed freshness depends on Drupal cache |
| Nature Biotechnology | Journal | Sitemap | Map | `https://www.nature.com/nbt/sitemap/2026/07/articles.xml` returns `200` + `application/xml` | Monthly sitemap can shift by month boundary; recent-month set must stay current |
| arXiv Quantitative Biology | Preprint | RSS | Map | `https://rss.arxiv.org/rss/q-bio` returns `200` + `application/rss+xml` | Feed can include revisions and cross-listings; dedupe must use normalized URL |
| bioRxiv | Preprint | RSS | Map | `https://connect.biorxiv.org/relate/feed/biorxiv.xml` returns `200` + `application/xml` | Feed may not expose all downstream revisions quickly |

## Additional Validated Sources

| Source | Primary Surface | Sample URL / Signal | Audit Outcome |
| --- | --- | --- |
| BioPharma Dive | RSS | `https://www.biopharmadive.com/feeds/news/` returns `200` + `application/rss+xml` | Cursor-capable |
| GEN – Genetic Engineering & Biotechnology News | RSS | `https://www.genengnews.com/feed/` returns `200` + `application/rss+xml` | Cursor-capable |
| Science | RSS | `https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science` returns `200` + `application/xml` | Cursor-capable |
| Endpoints News | Map | `https://endpoints.news/feed/` and `https://endpoints.news/rss` both return `403` | RSS blocked; remain map-first for now |
| BioCentury | Map | `https://www.biocentury.com/rss` returns `200` but `text/html`; `https://www.biocentury.com/feed/` ends in `404` | No reliable feed found; remain map-first |
| SynBioBeta | Map | `https://www.synbiobeta.com/feed` and `/rss.xml` both return `404` | No feed found; remain map-first |

## Gate Result

- Pilot family coverage achieved: news + journal + preprint all represented.
- Every pilot source has a primary surface and explicit map fallback.
- 8 of 11 enabled sources now have an explicitly audited primary surface; the remaining 3 have an explicit map-only decision rather than an implicit gap.
- Initial P2A implementation may proceed against the cursor-capable sources while map-only sources stay on conservative map routing.

## Notes

- This audit only verifies that the surfaces exist and are fetchable now.
- It does not yet certify long-term freshness quality or historical recall.
- Remaining non-pilot sources should stay on conservative map routing until their RSS/sitemap surfaces are separately verified.