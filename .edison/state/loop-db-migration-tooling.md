# Loop State: DB Migration 工具鏈建立

Goal: 為 BioMyne Koji 引入正式的 DB migration 工具鏈，取代「手動貼 SQL」：用 supabase CLI migration 管理 sql/001-006，追蹤已套用/未套用，防 schema drift 與重複執行炸 DB。達 strict 93 閘門。hackathon 式多 commit。
Started: 2026-09-20
Status: active
Quality Mode: strict (93)
Depth Level: L3 Deep Dive
Snapshot Cache: /Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji/docs/.project-context.md (STALE)
Snapshot Evidence Status: LOCATOR-ONLY
Budget: ~10 iterations

## 現況診斷（Neo 調查確認）

1. `supabase/` 目錄不存在（CLI 從未 init）
2. `supabase_migrations.schema_migrations` 不存在（無 migration history）
3. CLI 帳號無權限存取 `yihgpsbofjgoxbfypnia`（該 project 屬另一 org）
4. README 只說「Apply SQL migrations」但無實際流程
5. sql/001-006 手工套用、無版本追蹤、無 rollback

## 方案設計（供 PLAN 確認）

**核心選擇：supabase CLI migration（官方工具）**
- `supabase init` → 建立 supabase/ 目錄 + config.toml
- 把 sql/001-006 移入 `supabase/migrations/`（保留 sql/ 為鏡像或移轉）
- `supabase migration list` 看已套用/未套用
- `supabase db push` 套用未套用的 migrations（自動記錄到 schema_migrations）
- 需要：正確 org 的 CLI login token（用戶提供）

**阻擋點**：CLI 帳號權限 — 需用戶 `supabase login` 用正確 org 帳號 + 確認 project 可 link

## Stage Round Counters（v4.3）

| Stage | Current Round | Max Rounds | Status |
| --- | :---: | :---: | --- |
| DISCOVER（migration 工具鏈深研） | 1 | 2 | ✅ done（Neo 調查） |
| PLAN（方案設計：supabase CLI vs 替代） | 0 | 1 | 🔄 active |
| EXECUTE（init + migrations 移轉 + 文件） | 0 | 2 | pending |
| VERIFY（smith strict 93） | 0 | 3 | pending |

## Iterations

（待填）

## Circuit Breaker

Consecutive fails: 0/3
Budget: 0%
Status: HEALTHY