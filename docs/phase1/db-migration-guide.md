# DB Migration Guide

> **Last updated:** 2026-09-20
> **Scope:** BioMyne Koji — Phase 1 database migration tooling

## Why Migration Tooling?

Before this guide, all 6 SQL files (`sql/001`–`006`) were applied manually via Supabase SQL Editor. This creates three risks:

| Risk | Consequence |
|------|-------------|
| **No version tracking** | No way to know which migrations are applied on remote vs local |
| **Schema drift** | Manual edits in SQL Editor diverge from repo; next `db push` may fail or overwrite |
| **No rollback** | If a migration breaks something, no structured way to revert |

Supabase CLI migration (`db push`) solves all three: it records every applied migration in `schema_migrations`, detects drift, and enforces forward-only changes.

## Current State

| Item | Status |
|------|--------|
| `supabase/` directory | ✅ Initialized (`supabase init`) |
| `supabase/migrations/` | ✅ 6 timestamp-prefixed migration files (copied from `sql/`) |
| `sql/` directory | ⚠️ Retained as **read-only mirror** (see `sql/README.md`) |
| Remote DB | 001–005 applied manually; 006 applied manually; **no `schema_migrations` table yet** |
| `ops/scripts/db_migrate.sh` | ✅ Created |

## Migration Files

| Timestamp | Source | Description |
|-----------|--------|-------------|
| `20260920000000` | `sql/001` | Phase 1 core schema (6 tables + pgcrypto) |
| `20260920000010` | `sql/002` | Performance indexes |
| `20260920000020` | `sql/003` | Seed 3 biotech sources |
| `20260920000030` | `sql/004` | P2A incremental discovery state |
| `20260920000040` | `sql/005` | P2B refresh & category targets |
| `20260920000050` | `sql/006` | Crawl4AI source-level provider routing |

## First-Time Setup (after getting DB password)

All 6 migrations were already applied manually to the remote DB. Supabase CLI doesn't know this yet. You need to **baseline** the remote state before pushing anything new.

### Step 1: Set credentials

```bash
# Add to your .env (already in .env.example):
SUPABASE_DB_PASSWORD=<postgres-password-from-dashboard>
```

### Step 2: Dry-run to see what CLI thinks is pending

```bash
./ops/scripts/db_migrate.sh dry-run
```

You should see all 6 migrations listed as "pending" — because the CLI has no `schema_migrations` record yet.

### Step 3: Baseline — mark 001–005 as already applied

```bash
# Mark each migration as applied without actually running it
supabase migration repair --status applied 20260920000000
supabase migration repair --status applied 20260920000010
supabase migration repair --status applied 20260920000020
supabase migration repair --status applied 20260920000030
supabase migration repair --status applied 20260920000040
```

> **Why repair 001–005 only?** `006_crawl4ai_migration.sql` may not have been applied yet (check with SQL Editor: `SELECT * FROM schema_migrations;`). If it has, repair it too. If not, let `db push` apply it.

### Step 4: Push remaining migrations

```bash
./ops/scripts/db_migrate.sh dry-run   # should show only 006 (or nothing)
./ops/scripts/db_migrate.sh push      # apply with confirmation
```

### Step 5: Verify

```bash
./ops/scripts/db_migrate.sh list   # all should show as "Applied"
```

## Daily Workflow: Adding a New Migration

```bash
# 1. Create a new migration file (timestamp auto-generated)
./ops/scripts/db_migrate.sh new add_crawler_cost_column

# 2. Write your SQL in the generated file
#    Edit: supabase/migrations/<timestamp>_add_crawler_cost_column.sql

# 3. Dry-run to preview
./ops/scripts/db_migrate.sh dry-run

# 4. Apply
./ops/scripts/db_migrate.sh push
```

## Golden Rules

1. **NEVER edit schema directly in Supabase SQL Editor** — this causes `db push` sync errors. Always use migrations.
2. **NEVER edit a migration after it has been applied** — if you need to fix something, create a new migration that reverses + corrects (forward-fix).
3. **ALWAYS dry-run before push** — check what will be applied, especially after long gaps.
4. **Migration files are immutable once applied** — the `supabase/migrations/` directory is the source of truth.
5. **One logical change per migration** — don't bundle unrelated schema changes.

## Rollback Strategy

Supabase CLI does not support `migration down`. Recovery options:

| Scenario | Action |
|----------|--------|
| Bad migration, not yet pushed | Delete the file, create a corrected one |
| Bad migration, just pushed | Write a **forward-fix migration** that undoes the damage |
| Catastrophic data loss | Restore from Supabase PITR (Point-in-Time Recovery) backup |
| Schema drift detected | `supabase db push` will report drift; fix by aligning local migrations with remote |

## Troubleshooting

### "Error: schema drift detected"
Remote DB has changes that don't match local migrations. Fix: align local `supabase/migrations/` with remote, or use `supabase db reset` on dev.

### "Error: migration already applied"
The migration timestamp is already in `schema_migrations`. Don't re-apply. If the file was edited post-apply, create a new forward-fix migration.

### "password authentication failed"
`SUPABASE_DB_PASSWORD` is wrong. Get the correct one from Dashboard → Settings → Database → Connection string → Password.
