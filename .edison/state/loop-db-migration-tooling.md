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
### Iteration 1-3 — EXECUTE + VERIFY

- EXECUTE（trinity）：supabase init + sql/001-006 移入 supabase/migrations/（timestamp 前綴）+ db_migrate.sh + .env.example + guide（3 commits: e0f9dce/601ebb9/b2cc1f6）
- VERIFY R1（smith）：92.25 REPAIRABLE — CRA-001 High（guide 006 矛盾）/ CRA-002 Medium（percent-encode）/ CRA-003 Medium（list --db-url）/ CRA-004 Medium（P2 state）/ CRA-005/006 Low
- REPAIR（trinity）：6 findings 全修 + 掃同族（guide :8/:41）（3 commits: 6c1bef6/a034e07/41fb129）
- VERIFY R2（smith）：**95.20 PASS** — 6/6 FIXED、percent-encode libpq 4 組實測、--db-url 5 處、byte-identical 6/6、state 已同步；CRA-007 Low（guide CI note exit code 描述，不阻塞）

## 最終結果

**DB Migration 工具鏈建立完成 ✅（PASS 95.20/93）**
- supabase/migrations/：6 個 timestamp 前綴 migration（001-006，byte-identical）
- ops/scripts/db_migrate.sh：dry-run/push/list/new/status（Bash 3.2、percent-encoded、push confirm、help 免憑證）
- docs/phase1/db-migration-guide.md：首次 setup（repair 001-005 + push 006）+ 金律 + rollback
- 待用戶：提供 SUPABASE_DB_PASSWORD → 執行首次 setup（db push --dry-run → repair 001-005 → push 006）
- CRA-007（Low）：guide Step 4 CI note exit code 描述待修正（下次 touch 時）
