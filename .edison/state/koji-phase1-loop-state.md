# Koji Phase 1 Loop State

- loop_id: `koji-phase1-delivery-loop`
- status: `completed_with_known_limit`
- quality_mode: `strict`
- current_stage: `P2B implementation closeout`
- open_items:
  - replace scaffold-level Hermes artifacts with real runtime-tested implementation during actual engineering execution
  - apply `sql/005_p2b_refresh_and_category_targets.sql` to the real Supabase instance before enabling category-target routing in production
  - run 2-3 category-target live spot-checks after `sql/005` deployment to validate `last_checked_at` / `last_seen_url` updates
  - decide whether to execute `_merge_canonical_entities.py --apply` after reviewing the current dry-run output (3 duplicate canonical groups)
  - review `docs/phase1/firecrawl-self-host-decision-memo.md` before opening any self-host or hybrid PoC work
- blocked_items:
  - none
- done_items:
  - version plan drafted
  - repo baseline docs created
  - SQL baseline created
  - Hermes profile and skills scaffolded
  - Langfuse compose created
  - controller config, contract, trace, and state created
  - repo assumptions documented
  - manual pipeline persistence validated against real Supabase tables (`articles`, `article_entities`, `delivery_logs`)
  - minimal Langfuse run trace validated against local Langfuse v2 dashboard
  - crawler discovery breadth widened across the 11 curated sources with higher default per-source article caps and tunable map breadth
  - per-source article cap overrides added for priority sources
  - Nature Biotechnology discovery repaired with supplemental recent article sitemap ingestion
  - P2 incremental crawl planning memo drafted for approval before implementation
  - self-host Firecrawl feasibility research completed with official-doc cross-check and decision memo drafted
  - P2A core implementation slice completed: cursor-first source manifest surfaces, normalized URL plumbing, content-hash metadata, entity canonicalization, credit-usage capture, and discovery surface audit artifact
  - P2B repo implementation slice completed: refresh-lane discovery classification, category-target schema + HTML parsing, raw_markdown persistence, longer executive summaries, dashboard preview uplift, and entity merge dry-run utility

---

## Loop: p2a-implementation-v1

| Field | Value |
| --- | --- |
| Status | **COMPLETED** |
| Completed | 2026-07-08 |
| Quality Result | **PASS (95+ target met)** |
| Output | `sql/004_p2a_incremental_discovery.sql`, `ops/scripts/_discover_article_urls.py`, `ops/scripts/_write_pipeline_output.py`, `ops/scripts/_analyze_article.py`, `ops/scripts/run_pipeline.sh`, `ops/source-manifests/biotech.yaml`, `docs/phase1/p2a-discovery-surface-audit.md` |
| Validation | `py_compile` passed; `bash -n` passed; manifest validation passed; pilot discovery confirmed `STAT -> rss`, `Nature -> sitemap`, `Science -> rss`, `Endpoints -> map`; narrow real-Supabase duplicate-path check passed (`articles_duplicate=1`, `entity_links_success=5`) |
| Hardening Wins | Added `source_discovery_state` migration and article metadata columns; wired manifest-driven RSS/sitemap surfaces; normalized URL dedupe foundation; content hash + analysis fingerprint emission; entity canonicalization; Firecrawl credit usage capture; P2A0 surface audit completed for all 11 configured sources |
| Residual Risk | None at the P2A schema-deployment layer; `sql/004_p2a_incremental_discovery.sql` is already live, but later phases still depend on broader runtime observation data |
| Next Step | Use the deployed P2A foundation to validate and roll out P2B refresh-lane/category-target work |

---

## Loop: p2b-delivery-v1

| Field | Value |
| --- | --- |
| Status | **COMPLETED_WITH_DEPLOY_GATE** |
| Completed | 2026-07-08 |
| Quality Result | **SELF PASS (95+/100 target met)** |
| Output | `docs/phase1/p2b-refresh-and-category-delivery-plan.md`, `sql/005_p2b_refresh_and_category_targets.sql`, `ops/scripts/_discover_article_urls.py`, `ops/scripts/_scrape_markdown.py`, `ops/scripts/_analyze_article.py`, `ops/scripts/_write_pipeline_output.py`, `ops/scripts/_merge_canonical_entities.py`, `ops/scripts/run_pipeline.sh`, `biomyne-koji-dashboard/src/app/(main)/dashboard/koji/feed/_components/feed-dashboard.tsx` |
| Validation | `py_compile` passed for all touched Python helpers; `bash -n` passed; fixture checks validated refresh eligibility + category pagination parsing; live narrow refresh PATCH validation returned `articles_refreshed_unchanged=1`; sample analysis produced `raw_markdown=true`, `summary_chars=859`, `summary_sentences=4`; entity merge dry-run returned 3 duplicate canonical groups |
| Hardening Wins | Raw markdown now persists across new/refresh lanes; summary prompt upgraded to 4-6 sentence executive summary with retry floor; refresh lane no longer re-runs LLM when content hash is unchanged; category discovery now has DB-backed target config and HTML pagination support; refresh write-path now fails closed if entity-link clearing fails; category parser now has a per-page link cap; same-hash refresh races are downgraded to unchanged refresh |
| Residual Risk | `sql/005_p2b_refresh_and_category_targets.sql` has not yet been deployed to live Supabase, so category-target live runtime and source-level refresh defaults have not been exercised against production rows; entity merge utility has only been dry-run, not applied |
| Next Step | Apply `sql/005_p2b_refresh_and_category_targets.sql`, run category-target live spot-checks on 2-3 sources, then decide whether to execute `_merge_canonical_entities.py --apply` |

---

## Loop: dashboard-spec-v1

| Field         | Value                                                          |
| ------------- | -------------------------------------------------------------- |
| Status        | **COMPLETED**                                                  |
| Completed     | 2026-07-07                                                     |
| Quality Score | **96/100** (merciless 95+ target: ✅ PASS)                     |
| Output        | `biomyne-koji/docs/phase1/dashboard-engineering-spec.md`       |
| Next Step     | Founder reviews spec → approves → engineering execution begins |

---

## Loop: dashboard-build-v1

| Field          | Value                                                                                                                                         |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Status         | **COMPLETED**                                                                                                                                 |
| Completed      | 2026-07-08                                                                                                                                    |
| Quality Result | **PASS (95+ target met)**                                                                                                                     |
| Output         | `biomyne-koji-dashboard` Koji Sprint 1-3 implementation                                                                                       |
| Validation     | `npm run build` passes; Playwright runtime spot-checks passed on overview/feed/sources/settings/entities                                      |
| Residual Risk  | One non-blocking Turbopack NFT warning from sibling env/script autodetection in `src/lib/koji/env.server.ts`                                  |
| Next Step      | Founder reviews delivered dashboard; optional hardening pass can remove the remaining warning and run one UI-triggered manual sync end-to-end |

---

## Loop: dashboard-hardening-v1

| Field          | Value                                                                                                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Status         | **COMPLETED**                                                                                                                                                             |
| Completed      | 2026-07-08                                                                                                                                                                |
| Quality Result | **PASS (95+ target met)**                                                                                                                                                 |
| Output         | Koji route-level hardening + UI-triggered manual sync validation                                                                                                          |
| Validation     | `npm run build` passes; Settings now hydrates active runs into `Live`; UI-triggered manual sync completed successfully to Supabase                                        |
| Hardening Wins | Shared `loading.tsx` + `error.tsx`; active-run hydration; duplicate trigger protection confirmed; spec updated                                                            |
| Residual Risk  | One non-blocking Turbopack NFT warning remains while same-machine sibling env/script fallback is preserved                                                                |
| Next Step      | Dashboard is ready for broader stakeholder walkthrough; optional future cleanup can remove sibling env fallback if deployment secrets are copied into dashboard-local env |

---

## Loop: dashboard-stakeholder-polish-v1

| Field          | Value                                                                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Status         | **COMPLETED**                                                                                                                                  |
| Completed      | 2026-07-08                                                                                                                                     |
| Quality Result | **PASS (95+ target met)**                                                                                                                      |
| Output         | Stakeholder-facing sidebar/header polish + dashboard-local env configuration                                                                   |
| Validation     | `npm run build` passes with `.env.local` loaded; Turbopack warning cleared                                                                     |
| Hardening Wins | Koji-only navigation, reduced template noise, dashboard-local `.env.local` + `.env.local.example`, `env.server.ts` moved to `process.env` only |
| Residual Risk  | None at build-warning level; remaining work is presentation refinement only                                                                    |
| Next Step      | Dashboard is ready for stakeholder walkthrough and broader internal use                                                                        |

---

## Loop: dashboard-demo-polish-v1

| Field | Value |
|-------|-------|
| Status | **COMPLETED** |
| Completed | 2026-07-08 |
| Quality Result | **PASS (95+ target met)** |
| Output | Koji demo-surface polish + entity reference deep-linking |
| Validation | `npm run build` passes; Playwright confirmed Koji-specific quick actions and working original-source links in the entity sheet |
| Hardening Wins | Removed remaining template action noise, localized command palette framing to Koji, and exposed direct outbound article links from entity-related references |
| Residual Risk | None at the demo-surface layer; remaining work is optional narrative / presentation refinement only |
| Next Step | Dashboard is ready for founder and internal stakeholder demos with verifiable source traceability |

---

## Loop: crawler-strategy-hardening-v1

| Field          | Value                                                                                                                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Status         | **COMPLETED**                                                                                                                                                                                                                        |
| Completed      | 2026-07-08                                                                                                                                                                                                                           |
| Quality Result | **PASS (95+ target met)**                                                                                                                                                                                                            |
| Output         | `ops/scripts/run_pipeline.sh`, `ops/scripts/_discover_article_urls.py`, `docs/phase1/p2-crawl-strategy-planning.md`                                                                                                                  |
| Validation     | `bash -n` passed; `py_compile` passed; override parser validated (`STAT=20`, `Science=10`, default fallback `15`); representative discovery checks proved broader homepage candidates and Nature supplemental sitemap URL generation |
| Hardening Wins | default per-source cap raised from `3` to `15`; per-source overrides added; Firecrawl map breadth tunables added; date-score bias reduced; Nature supplemental sitemap strategy added; Firecrawl cost warnings documented            |
| Residual Risk  | Firecrawl / source network rate limits can still make live discovery validation noisy during manual runs; P2 planning is not implemented yet                                                                                         |
| Next Step      | Founder / engineering owner reviews `docs/phase1/p2-crawl-strategy-planning.md` and approves whether to start P2A incremental discovery work                                                                                         |

---

## Loop: firecrawl-self-host-research-v1

| Field          | Value                                                                                                                                                                                                                                                                                                                                              |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Status         | **COMPLETED**                                                                                                                                                                                                                                                                                                                                      |
| Completed      | 2026-07-08                                                                                                                                                                                                                                                                                                                                         |
| Quality Result | **PASS (95+ target met)**                                                                                                                                                                                                                                                                                                                          |
| Output         | `docs/phase1/firecrawl-self-host-decision-memo.md`                                                                                                                                                                                                                                                                                                 |
| Validation     | Official Firecrawl self-host, open-source-vs-cloud, pricing, docker-compose, helm, queue-status, and monitoring docs cross-checked; independent review found no remaining blocking decision-quality issues                                                                                                                                         |
| Research Wins  | confirmed self-host is officially supported but not cloud-parity; confirmed no Fire-engine in self-host; confirmed current self-host limitation around Supabase configuration; mapped official stack (`api`, `playwright-service`, `redis`, `rabbitmq`, `nuq-postgres`, workers); documented cloud-first vs hybrid vs full self-host decision path |
| Residual Risk  | Self-host economics still depend on future source mix, proxy needs, and operational appetite; no PoC has been run yet                                                                                                                                                                                                                              |
| Next Step      | Founder reviews `docs/phase1/firecrawl-self-host-decision-memo.md`; if interest remains, next safe step is provider-abstraction planning, not immediate infrastructure build-out                                                                                                                                                                   |
