# Loop State: Dashboard Crawl4AI 整合

Goal: 為 Dashboard 前端補上 Crawl4AI 遷移的最新功能（`crawler_provider` routing 顯示 + 控制），讓用戶可在前端實際測試和使用。修改 6 層：types/form/schema/data/api/ui。達 strict 93 閘門。hackathon 式多 commit。
Started: 2026-09-20
Status: active
Quality Mode: strict (93)
Depth Level: L3 Deep Dive
Snapshot Cache: STALE（LOCATOR-ONLY）
Budget: ~12 iterations

## 現狀（DISCOVER 確認）
- `crawler_provider` 0 命中 — P0-P4 新功能完全未反映到前端
- DB `sources` 表已有 `crawler_provider` 欄位（P2 migration 已落地）
- Supabase REST `select=*` 會自動帶回 `crawler_provider` → data 層只需 normalize
- 前端設計風格：Next.js App Router + shadcn/ui（Button/Dialog/Select/Table/Field）+ Supabase REST mode + tanstack cache

## 6 層修改範圍（spec §1.2 #1 + §5 保守延伸）
1. `types.ts`：KojiSource + crawlerProvider
2. `source-form.ts`：schema + form values
3. `schema.ts`：drizzle DB schema + crawlerProvider
4. `data.server.ts`：RestSourceRow + normalizeSource + createSource/updateSource + listSources
5. `api/koji/sources`：POST/PATCH handle crawlerProvider
6. `sources-dashboard.tsx`：table column + form Select（'local'|'firecrawl_cloud'）

## Stage Round Counters

| Stage | Round | Max | Status |
| --- | :---: | :---: | --- |
| EXECUTE（6 層整合） | 0 | 2 | pending |
| EXECUTE（overview 卡片） | 0 | 1 | pending |
| VERIFY | 0 | 3 | pending |

## Iterations

（待填）

## Circuit Breaker

Consecutive fails: 0/3
Budget: 0%
Status: HEALTHY