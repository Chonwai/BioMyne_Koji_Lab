# P2A0 Discovery Surface Audit

## Status

| Field | Value |
| --- | --- |
| Status | Completed for all 11 configured sources |
| Date | 2026-07-09 |
| Scope | 5 pilot sources + 6 additional validated sources |
| Purpose | Satisfy P2A0 gate before P2A implementation, then capture live-runtime surface corrections discovered during the 2026-07-09 hotfix loop |

## Pilot Set

| Source | Family | Primary Surface | Fallback Surface | Sample URL / Signal | Known Failure Mode |
| --- | --- | --- | --- | --- | --- |
| STAT News | News | RSS | Map | `https://www.statnews.com/feed/` returns `200` + `application/rss+xml` | Feed temporarily stale or cached behind CDN |
| Fierce Biotech | News | RSS | Map | `https://www.fiercebiotech.com/rss/xml` returns `200` + `application/rss+xml` | Feed freshness depends on Drupal cache |
| Nature Biotechnology | Journal | Sitemap | Map | `https://www.nature.com/nbt/sitemap/2026/07/articles.xml` returns `200` + `application/xml` | Monthly sitemap can shift by month boundary; recent-month set must stay current |
| arXiv Quantitative Biology | Preprint | RSS | Map | `https://rss.arxiv.org/rss/q-bio` returns `200` + `application/rss+xml` | Feed can include revisions and cross-listings; dedupe must use normalized URL |
| bioRxiv | Preprint | Category Page | Map | `https://www.biorxiv.org/content/early/recent` returns `200` + public HTML listing with `/content/10.x` article links | Generic feed endpoint was unreliable / empty in current runtime; DOI prefix is no longer safely assumed to be only `10.1101` |

## Additional Validated Sources

| Source | Primary Surface | Sample URL / Signal | Audit Outcome |
| --- | --- | --- |
| BioPharma Dive | RSS | `https://www.biopharmadive.com/feeds/news/` returns `200` + `application/rss+xml` | Cursor-capable |
| GEN – Genetic Engineering & Biotechnology News | RSS | `https://www.genengnews.com/feed/` returns `200` + `application/rss+xml` | Cursor-capable; article URLs currently live under `/topics/{vertical}/{slug}` and must not be over-filtered as taxonomy pages |
| Science | RSS | `https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science` returns `200` + `application/xml` | Cursor-capable; feed is RSS 1.0 / RDF rather than RSS 2.0 |
| Endpoints News | Map | `https://endpoints.news/feed/` and `https://endpoints.news/rss` both return `403` | RSS blocked; remain map-first for now |
| BioCentury | RSS | `https://www.biocentury.com/rss/BioCentury.xml` returns `200` + `application/xml` | Cursor-capable; article pages still partial/paywalled downstream |
| SynBioBeta | Category Page | `https://www.synbiobeta.com/synthetic-bio-news` exposes public `/read/` article links | No reliable feed found; listing-first with map fallback |

## Gate Result

- Pilot family coverage achieved: news + journal + preprint all represented.
- Every pilot source has a primary surface and explicit map fallback.
- All 11 enabled sources now have an explicitly audited primary surface, including listing-first and map-first exceptions.
- Initial P2A implementation may proceed against the cursor-capable sources while map-only sources stay on conservative map routing.

## Notes

- This audit only verifies that the surfaces exist and are fetchable now.
- It does not yet certify long-term freshness quality or historical recall.
- Map-first exceptions currently remain `Endpoints News` only; `BioCentury` and `SynBioBeta` were upgraded during the 2026-07-09 runtime hotfix after independent verification.