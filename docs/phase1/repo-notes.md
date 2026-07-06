# Phase 1 Repo Notes

## Purpose

This note records important implementation assumptions for the Phase 1 baseline repo.

## 1. SQL Assumption

The SQL files in `sql/` are written for PostgreSQL / Supabase PostgreSQL.

- `001_phase1_core_schema.sql` assumes PostgreSQL extensions such as `pgcrypto`
- `002_phase1_indexes.sql` assumes standard PostgreSQL indexing
- `003_seed_sources.sql` is written in a conservative `insert ... select ... where not exists` style to reduce compatibility noise in generic SQL tooling

## 2. Hermes Assumption

The files under `hermes/` are scaffold and configuration artifacts, not guaranteed drop-in runtime code.

They are intended to:

- standardize the Phase 1 structure
- reduce ambiguity for the engineering owner
- avoid inventing unsupported runtime APIs

## 3. Model Assumption

The exact Ollama model tag is intentionally left open until Week 1 smoke testing.

Do not hard-code a model until:

1. it pulls successfully
2. it responds successfully
3. it can emit schema-valid JSON for the Phase 1 prompt

## 4. Scope Rule

If implementation work starts to require any of the following, stop and escalate:

- GraphDB / Neo4j
- FastAPI BFF
- Next.js dashboard
- second crawler layer
- broader auth / RBAC system
