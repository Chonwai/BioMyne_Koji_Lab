# sql/ — Read-Only Mirror

> **⚠️ This directory is a read-only mirror.**
> Migrations have moved to `supabase/migrations/` (timestamp-prefixed).
> Do NOT apply these files directly to the database — use `supabase db push` instead.

## Files

| File | Description | Migration (canonical) |
|------|-------------|----------------------|
| `001_phase1_core_schema.sql` | Phase 1 core tables (sources, crawl_runs, articles, entities, article_entities, delivery_logs) | `20260920000000_001_phase1_core_schema.sql` |
| `002_phase1_indexes.sql` | Performance indexes | `20260920000010_002_phase1_indexes.sql` |
| `003_seed_sources.sql` | Seed 3 biotech sources | `20260920000020_003_seed_sources.sql` |
| `004_p2a_incremental_discovery.sql` | P2A incremental discovery state | `20260920000030_004_p2a_incremental_discovery.sql` |
| `005_p2b_refresh_and_category_targets.sql` | P2B refresh & category delivery | `20260920000040_005_p2b_refresh_and_category_targets.sql` |
| `006_crawl4ai_migration.sql` | Crawl4AI source-level provider routing | `20260920000050_006_crawl4ai_migration.sql` |

## Why keep this mirror?

- Human-readable index for code review (numbered prefix is easier to scan than timestamps)
- Quick reference for `run_pipeline.sh` which calls these directly in dev mode
- Content is identical to `supabase/migrations/` — verified by `diff`
