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
| EXECUTE-I2（B-3 sql/006 + B-2 routing） | 1 | 2 | ✅ done（Iteration 2 — 2 commits，7-case 語意測試 7/7 PASS） |
| EXECUTE-I3（B-4 環境 + B-1 POC + P0 實測） | 1 | 2 | ✅ done（Iteration 3 — 3 commits，未知數 1 已回答） |
| VERIFY（smith strict 93） | 2 | 3 | ✅ **R1 90.4 REPAIRABLE → R2 93.75 PASS** |
| REPAIR（trinity bounded） | 1 | 2 | ✅ done（H-1/H-2/L-1 全修） |

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

### Iteration 2 — EXECUTE-I2（trinity B-3 + B-2）

**Agent: trinity** — 2 commits：
- `60b1b71` feat(sql): add 006 crawl4ai migration — `alter table sources add column if not exists crawler_provider text not null default 'local'` + seed 3 hard sources（名稱與 sql/003 L44/50/56 吻合）；沿用小寫慣例
- `93746c0` feat(pipeline): crawler_provider routing — L204 pre-flight 放寬（CRAWLER_ALLOW_CLOUD=false 跳過 FIRECRAWL_KEY hard-fail）、L258 select 11 欄、L302–308 三層決策（kill-switch > DB > env；`$line` 為現有 JSON 變數）+ log 一行
- `bash -n` 通過；isolated sandbox 7-case 語意測試 7/7 PASS（kill-switch 壓過 DB/env、DB 值 honored、空值→env→local）
- 偏離標記：2b env fallback 採 spec §4.3 正規版（DB 缺值→env→local），非 user 範例的 or 'local'；範圍錨定遵守（crawler_providers.py 留 P1）

**Outcome: I2 ✅ → EXECUTE-I3（B-4 環境重建 + P0 實測）**

### Iteration 3 — EXECUTE-I3（trinity B-4 + B-1 + P0）

**Agent: trinity** — 3 commits：
- `9ecd885` chore(dev): requirements-dev.txt 加 crawl4ai==0.9.3/playwright/trafilatura/pytest/PyYAML/langfuse（.venv 已建，Python 3.12.9 避 3.13 greenlet）
- `8b1b1c8` fix(poc): 對齊 v0.9.3 API + CLI（`args.llm`、移除不存在的 `CrawlerRunConfig(llm_config=...)`）
- `01033e6` docs: `docs/phase1/crawl4ai-poc-verification.md`（153 行 P0 實測證據）
- **P0 實測**：markdown-only success（status 200, word_count 2173）；Ollama LLM extraction 端到端跑通（完整合法 JSON：title/summary/priority_level/entities 四型齊全）
- **關鍵發現：單篇 LLM extraction 首輪 ~9.5min / warm ~5.4min**（Ollama prefix cache 命中 9348/9352）— 遠慢於 Firecrawl 秒級，P1 延遲預算必須納入
- 環境注意：zsh `python3` alias 劫持 venv → 用 `.venv/bin/python3`；.venv 已入 .gitignore
- 實測 URL 偏離（虛構 DOI 404→真實 preprint 10.1101/2024.05.21.595135v1）、POC CLI 預設 markdown-only 已標記

**未知數 1 ✅ 已回答：Crawl4AI 0.9.3 新 API + Ollama qwen3.6:35b-mlx（MLX 100% GPU）端到端跑通。**

**Outcome: I3 ✅ → VERIFY（smith strict 93，全變更審查）**

### Iteration 4 — VERIFY R1（edison-doc-reviewer，smith 網路失敗後替代）

**Measured Score: 90.4/100 → REPAIRABLE**（D1=90 D2=88 D3=85 D4=88 D5=95 D6=92 D7=95）
- 3 findings：**H-1**（spec §3:106 `CrawlerRunConfig(llm_config=...)` 錯誤寫法 — 同批次 POC 實測證實 TypeError）、**H-2**（evaluation memo L130 舊式 API 殘留，掃同類）、**L-1**（poc-verification commits 表待填 hash）
- 正面：sql/006 正確、routing 三層決策正確、P0 數字全數實測複核吻合
- 一票決：N（修復後可放行）

### Iteration 5 — REPAIR（trinity H-1/H-2/L-1）
- `fef238a` fix(spec): H-1 §3 LLMConfig 用法修正（與 §4.2/Step 3 POC 驗證模式一致）
- `70f714f` fix(memo): H-2 evaluation memo 舊式 API 修正
- `d8bb9e8` docs(poc): L-1 commit hash 填入 `01033e6`
- 掃同類：`CrawlerRunConfig(llm_config=`/`LLMExtractionStrategy(provider=` 僅剩記錄性命中（poc-verification/feasibility-review 的 before 描述），正確保留

### Iteration 6 — VERIFY R2（edison-doc-reviewer 複審）

**Measured Score: 93.75/100 → PASS**（DR-D1=95 D2=96 D3=94 D4=95 D5=90 D6=90 D7=93；加權 93.75）
- 上輪 3 findings 全數驗證修復（diff 實證）；§3/§4.2/Step 3 三處新 API 完全一致
- 掃同類：零活躍殘留；新 finding 僅 L-2（Low 觀察項：spec 可補 LLM extraction 完整鏈路說明，不阻塞）
- 一票決：**Y — 可作為 P1 開發通過閘**

**Neo 決策：93.75 ≥ 93 → PASS → DELIVER**（Stop Rule 不觸發；L-2 記錄供 P1 參考）

## 最終交付物

| # | 類別 | 內容 | commits |
| --- | --- | --- | --- |
| 1 | 文檔修正 | spec F-1..F-6（API 新寫法/AC-1 下修/select 註/Python3.12/content_hash）+ overview F-5 | `706917a` `e236a54` `38badb4` `8c2d710` `83952cc` + `fef238a` |
| 2 | SQL | `sql/006_crawl4ai_migration.sql`（crawler_provider 欄位 + seed 3 hard sources） | `60b1b71` |
| 3 | Pipeline | `run_pipeline.sh` select 11 欄 + 三層決策 + pre-flight 放寬（7-case 測試 7/7） | `93746c0` |
| 4 | POC | `crawl4ai_poc.py` 還原 + 對齊 v0.9.3 API（`8b1b1c8`） | `453a555` `8b1b1c8` |
| 5 | 環境 | `.venv`（Python 3.12.9）+ requirements-dev.txt（crawl4ai==0.9.3 等） | `9ecd885` |
| 6 | P0 證據 | `docs/phase1/crawl4ai-poc-verification.md`（153 行） | `01033e6` `d8bb9e8` |

**Loop 總 commits：15 個**（ccbf090 → 706917a → e236a54 → 38badb4 → 8c2d710 → 83952cc → 453a555 → 60b1b71 → 93746c0 → 9ecd885 → 8b1b1c8 → 01033e6 → fef238a → 70f714f → d8bb9e8 → 04059df）

## 關鍵成果（供下一輪 P1 參考）

- **未知數 1 ✅ 已回答**：Crawl4AI 0.9.3 新 API + Ollama qwen3.6:35b-mlx（MLX 100% GPU）端到端跑通 LLM extraction（完整合法 JSON）
- **⚠️ 延遲警示**：單篇 LLM extraction 首輪 ~9.5min / warm ~5.4min（Ollama prefix cache 命中 9348/9352）— 遠慢於 Firecrawl 秒級；P1 需設計每篇延遲預算（本地 0 成本 + 資料不出機器的取捨）
- **未知數 2 未回答**：8 easy sources 反爬現況（STAT/Fierce 已知 Cloudflare）→ P1 前需 P0 逐一實測
- **L-2 觀察**：spec 可補 LLM extraction 完整鏈路說明

## Circuit Breaker

Consecutive fails: 0/3
Budget: 45%
Status: HEALTHY（Loop complete ✅）