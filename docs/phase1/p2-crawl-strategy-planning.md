# P2 Crawl Strategy Planning Memo

## Status

| Field | Value |
| --- | --- |
| Status | Draft for founder / engineering approval |
| Scope | P2 planning only, no implementation |
| Updated | 2026-07-08 |
| Baseline | Phase 1 Bash + Python helpers + Supabase |

## 1. Why This Memo Exists

Phase 1 now discovers broader article candidates across all 11 curated sources, but it still relies on repeated discovery work that can consume Firecrawl credits inefficiently over time.

This memo defines the recommended P2 direction for:

- incremental crawling
- category / tag page crawling
- Firecrawl credit budget management
- avoiding duplicate map, scrape, and LLM analysis work

## 2. Current State After P0/P1 Hardening

### Implemented now

- default `MAX_ARTICLES_PER_SOURCE` raised from `3` to `15`
- per-source overrides supported via `MAX_ARTICLES_PER_SOURCE_OVERRIDES`
- discovery breadth tunable via `DISCOVERY_MAP_LIMIT_MULTIPLIER` and `DISCOVERY_MAP_MIN_LIMIT`
- freshness bias reduced via `DISCOVERY_DATE_SCORE_BONUS`
- Nature Biotechnology supplemented with recent article sitemap discovery

### Already present before P2

- discovery-time exact URL dedupe via `article_exists(url)`
- database-level exact URL dedupe via `articles.url` unique constraint
- duplicate URLs therefore skip both scrape persistence and repeat LLM analysis in the current pipeline path

### Remaining inefficiency

The main recurring cost is repeated discovery itself, especially repeated `map` work against sources that have already been mined recently.

## 3. Verified External Facts

The following points were independently cross-checked against current Firecrawl documentation during this loop:

- Firecrawl `changeTracking` exists on `/v2/scrape` and can return `new`, `same`, `changed`, or `removed`
- `changeTracking` basic mode and `git-diff` mode do not add extra cost beyond standard scrape credits
- `changeTracking` `json` mode costs `5 credits per page`
- `changeTracking` bypasses index cache and ignores `maxAge`
- Firecrawl `map` supports `sitemap` modes `skip`, `include`, and `only`
- Firecrawl `map` exposes `ignoreCache`, and sitemap data is cached for up to 7 days
- Firecrawl exposes a credit usage endpoint at `GET /v1/team/credit-usage`

## 4. Recommended P2 Design

### P2A: Incremental Discovery First

Replace `map-first every run` with `cursor-first discovery`.

Recommended priority order per source:

1. RSS / Atom feed cursor
2. sitemap `lastmod` cursor or sitemap URL reconciliation
3. category / TOC page cursor
4. Firecrawl `map` only as fallback or scheduled reconciliation

Key idea:

- `map` should no longer be the default for every source on every run
- `map` should be used on bootstrap, fallback, or weekly reconciliation only

### P2B: Separate New URL Discovery From Known URL Refresh

Split pipeline behavior into two lanes:

- `new URL discovery lane`
- `known URL refresh lane`

Rules:

- new URLs go through normal scrape + analysis flow
- known URLs are not re-analyzed automatically unless they are selected for refresh
- refresh should target only recent or revision-prone sources such as preprints and journals

### P2C: Hash-Based LLM Skip

When a known URL is refreshed:

1. scrape page content
2. normalize markdown
3. compute `content_hash`
4. if hash unchanged, skip LLM analysis
5. if hash changed, rerun summary / tagging / entity extraction

This is the highest-value protection against repeat LLM cost once refresh behavior exists.

## 5. Category / Tag Page Strategy

For media sites that do not provide a reliable feed or high-quality sitemap surface:

- define 1-3 high-signal category pages per source
- rotate them instead of crawling the homepage only
- stop scanning when the crawler reaches `last_seen_url` or clearly older `published_at`

Examples:

- biotech
- research
- funding
- partnerships
- therapeutics
- current issue / latest articles / early release pages

This is more controllable than site-wide `map` and usually closer to how editorial sites organize high-value content.

## 6. Firecrawl Budget Modes

Add explicit run-time budget modes:

### `normal`

- run feed / sitemap / category discovery
- allow bounded refreshes
- allow scheduled reconciliation map

### `conserve`

- disable reconciliation map
- keep only highest-priority sources
- reduce refresh volume

### `critical`

- run only cheapest cursor-based discovery surfaces
- no refresh lane
- no reconciliation map

Recommended per-run counters:

- `max_map_calls_per_run`
- `max_scrapes_per_run`
- `max_refresh_scrapes_per_run`
- `remaining_credits_before`
- `remaining_credits_after`

## 7. Minimum Schema / State Additions

### New table: `source_discovery_state`

Suggested columns:

- `source_id`
- `cursor_type`
- `last_discovery_at`
- `last_cursor_published_at`
- `last_cursor_url`
- `last_map_at`
- `last_sitemap_checkpoint`
- `cooldown_until`

### New table: `source_category_targets`

Suggested columns:

- `source_id`
- `name`
- `url`
- `priority`
- `enabled`
- `last_seen_url`
- `last_seen_published_at`
- `last_checked_at`

### New columns on `articles`

- `source_published_at`
- `discovery_method`
- `last_scraped_at`
- `content_hash`
- `analysis_version`
- `analysis_fingerprint`
- `last_analyzed_at`

### New columns on `crawl_runs`

- `remaining_credits_before`
- `remaining_credits_after`
- `budget_mode`
- `map_calls`
- `scrape_calls`
- `refresh_scrape_calls`

### Optional debug artifact

- `.pipeline/state/discovery/*.json`

This should be debug-only, not the source of truth.

## 8. What Not To Build Yet

Do not widen to:

- Redis / Kafka / queue infrastructure
- semantic near-duplicate clustering across sources
- full-site frontier crawler orchestration
- generalized ETag / Last-Modified framework for every source
- Firecrawl `changeTracking` JSON mode as a default path

Reason:

These add complexity faster than they reduce cost at current Phase 1 scale.

## 9. Recommended Roadmap

### P2A

- add `source_discovery_state`
- implement cursor-first discovery
- move `map` to fallback / reconciliation mode
- add credit usage capture at run start and end

Validation:

- article recall remains acceptable on 3-5 pilot sources
- map call count drops materially versus current baseline

### P2B

- add `source_category_targets`
- implement category / TOC rotation
- add known URL refresh lane

Validation:

- refreshed same-URL articles detect meaningful changes
- homepage-only blind spots shrink on at least 2 editorial sources

### P2C

- add `content_hash` and analysis fingerprints
- skip repeat LLM analysis when content hash is unchanged
- add budget modes and per-run caps

Validation:

- LLM calls per run drop on repeat schedules
- monthly Firecrawl and LLM spend becomes predictable

## 10. Decision Recommendation

Approve P2A first.

Why:

- it attacks the real waste source: repeated discovery
- it preserves current architecture
- it creates the state foundation required for P2B and P2C

P2B should follow only after 3-5 sources confirm the cursor-first design is stable.

P2C should follow once refresh behavior exists and real repeat-content patterns can be observed.

## 11. Approval Questions

Before implementation starts, confirm:

1. Which 3-5 sources are the first P2A pilot set?
2. Which sources are allowed into the known URL refresh lane?
3. What monthly Firecrawl credit budget should trigger `conserve` mode?
4. Is `source_discovery_state` acceptable as a Phase 1.5 schema extension on Supabase?
