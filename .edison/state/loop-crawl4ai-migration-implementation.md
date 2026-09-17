# Loop State: Crawl4AI 遷移前置補實（Fixes + Gaps + P0 PoC）

Goal: 執行可行性調查報告（PASS 93）建議的前置工作並驗證通過：(1) F-1..F-6 修正兩份權威文檔（spec/overview）的 blocking 錯誤；(2) B-1..B-4 缺口補實（POC API 修正、sql/006 + run_pipeline routing、環境重建）；(3) P0 最小驗證跑通（新 API + Ollama LLM extraction 端到端）。**通過後下一輪才展開 P1 Provider Abstraction 正式開發。** hackathon 式多 commit。
Started: 2026-09-18
Status: active
Quality Mode: strict (93)
Depth Level: L3 Deep Dive
Snapshot Cache: /Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji/docs/.project-context.md (STALE)
Snapshot Evidence Status: LOCATOR-ONLY — 快取僅供定位，Critical findings 必須實時 scan 驗證
Budget: ~16 iterations

## Stage Round Counters（v4.3）

| Stage | Current Round | Max Rounds | Status |
| --- | :---: | :---: | --- |
| EXECUTE-I1（文檔修正 F-1..F-6） | 1 | 2 | ✅ done（Iteration 1 — 5 commits） |
| EXECUTE-I2（B-3 sql/006 + B-2 routing） | 0 | 2 | pending |
| EXECUTE-I3（B-4 環境 + B-1 POC + P0 實測） | 0 | 2 | pending |
| VERIFY（smith strict 93） | 0 | 3 | pending |
| REPAIR（trinity bounded） | 0 | 2 | pending |

## 任務形態與範圍

- Loop C（Full Dev）— EXECUTE（trinity）→ VERIFY（smith）；Maker ≠ Checker ✓
- **範圍錨定**：crawler_providers.py 完整實作 = P1（下一輪）。本輪只做：
  - F-1..F-6 文檔修正（spec §3/§4.2/Step 3/Step 4/Step 5/AC-1/§9 + overview §4）
  - B-3：sql/006_crawl4ai_migration.sql（crawler_provider 欄位）
  - B-2：run_pipeline.sh select 11 欄 + 三層 provider 決策（PROVIDER 變數選定邏輯；實際 provider 呼叫留 P1）
  - B-4：venv + 安裝 crawl4ai/playwright/trafilatura/pytest + playwright install chromium + requirements-dev.txt 更新
  - B-1：crawl4ai_poc.py 舊式 API → 新 API（LLMConfig + content_filter）
  - P0 最小驗證：修好的 POC 抓 bioRxiv 公開頁，LLM extraction 用 Ollama 跑通（回答未知數 1）

## Iterations

### Iteration 1 — EXECUTE-I1（trinity 文檔修正 F-1..F-6）

**Agent: trinity** — 5 commits，F-1..F-6 全數落地並 grep 驗證：
- `706917a` docs(spec): F-1 Crawl4AI v0.9.x API fix（§3 L106 / §4.2 L162 / Step 3 L264）
- `e236a54` docs(spec): F-2 AC-1 目標下修（Step 5 L319 / §7 AC-1 L358）
- `38badb4` docs(spec): F-3 select 註（L291）+ F-4 Python 3.12/DYLD（L225/L410）
- `8c2d710` docs(overview): F-5 stealth vendor benchmark 註記（§4 P1 L104）
- `83952cc` docs(spec): F-6 content_hash normalize 建議（L321）
- Self-audit mirror：CR-D1..D7 全過（文檔任務 N/A 項標記）
- 回報 pre-existing dirty state：`ops/poc/crawl4ai_poc.py`（非本次所改）

**B-1 簡化決策（Neo 調查確認）**：`git log` 顯示 HEAD（`f8d52b9`）已把 POC 改成 v0.9.x 新 API；dirty state 是把 POC **倒退成舊式 API** 的未 commit 改動。→ B-1 = `git checkout` 還原 dirty state（最小修復），非重寫。

**Outcome: I1 ✅ → EXECUTE-I2（B-3 + B-2）**

## Circuit Breaker

Consecutive fails: 0/3
Budget: 8%
Status: HEALTHY