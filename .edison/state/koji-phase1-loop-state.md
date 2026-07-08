# Koji Phase 1 Loop State

- loop_id: `koji-phase1-delivery-loop`
- status: `completed_with_known_limit`
- quality_mode: `strict`
- current_stage: `self-host firecrawl research closeout`
- open_items:
  - replace scaffold-level Hermes artifacts with real runtime-tested implementation during actual engineering execution
  - approve `docs/phase1/p2-crawl-strategy-planning.md` (cloud-first P2 plan) and answer its approval questions before starting P2A implementation
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
