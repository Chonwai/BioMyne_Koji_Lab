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
| EXECUTE-I1（文檔修正 F-1..F-6） | 0 | 2 | pending |
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

（待填）

## Circuit Breaker

Consecutive fails: 0/3
Budget: 0%
Status: HEALTHY