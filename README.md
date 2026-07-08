# BioMyne Koji Phase 1 Repository

## Purpose

This repository contains the Phase 1 implementation baseline for BioMyne Koji.

Phase 1 is a **viability validation loop**, not a full product build. The goal is to establish a working intelligence workflow using Hermes Agent, Firecrawl, Ollama, Supabase, and Langfuse.

## What This Repo Contains

- repo-local planning and execution documents
- SQL migration baseline for Supabase
- Hermes profile and skill scaffolds
- source manifest template
- bootstrap / validation scripts
- observability baseline
- operations runbook

## What This Repo Does Not Contain Yet

- FastAPI BFF
- Next.js dashboard
- GraphDB / Neo4j
- GraphRAG
- production-grade multi-user auth
- full frontend application

## Repo Structure

```text
biomyne-koji/
  README.md
  .env.example
  docs/
    phase1/
  hermes/
    profiles/
    skills/
  ops/
    source-manifests/
    scripts/
  sql/
  observability/
    langfuse/
```

## Phase 1 Operating Rule

If a task naturally expands toward dashboarding, GraphDB, or a second runtime layer, stop and escalate. Do not widen scope inside Phase 1.

## Recommended Execution Order

1. Read `docs/phase1/engineering-spec.md`
2. Read `docs/phase1/v1.0-phase1-delivery-plan.md`
3. Fill `.env.example`
4. Apply SQL migrations to Supabase
5. Configure Hermes profile
6. Validate source manifest
7. Run one manual end-to-end loop
8. Enable scheduled runs only after smoke checks pass

## Crawl Strategy Knobs

The manual pipeline now supports repo-local crawl tuning without code changes:

- `MAX_ARTICLES_PER_SOURCE`: default candidate cap per source (default `15`)
- `MAX_ARTICLES_PER_SOURCE_OVERRIDES`: comma-separated per-source overrides, for example `STAT News=20,Nature Biotechnology=18`
- `DISCOVERY_MAP_LIMIT_MULTIPLIER` and `DISCOVERY_MAP_MIN_LIMIT`: widen Firecrawl `/v2/map` discovery breadth before ranking
- `DISCOVERY_MIN_CANDIDATE_SCORE`: lower or tighten the candidate score cutoff
- `DISCOVERY_DATE_SCORE_BONUS`: controls how strongly fresh URL date patterns dominate ranking

This keeps Phase 1 local and simple while allowing broader article discovery across the 11 curated sources.

Use these knobs carefully: broader discovery can raise Firecrawl credit burn quickly, especially when `DISCOVERY_MAP_LIMIT_MULTIPLIER` is set aggressively across all 11 sources.
