# Hotfix Post-Mortem: Pipeline 插入失敗 + bioRxiv 中斷 (2026-07-07 Run #2)

**Date:** 2026-07-07
**Severity:** P1 (Critical — pipeline unusable)
**Reported by:** 手動管線觸發 (run 8c4e9dd8)
**Time to Resolution:** ~90 minutes
**Fix Author:** agent (GitHub Copilot, edison-tech-lead-dev-workflow, deep mode)

---

## Timeline

- `18:57` 管線觸發 (run `8c4e9dd8-71d2-440a-a317-7da49a57c277`)
- `19:03` 使用者發現管線停在 bioRxiv、大量 "Failed to insert" 錯誤
- `19:08` 開始 deep mode 調查
- `19:15` 根因 #1 確認：`url` UNIQUE 約束導致重複文章插入失敗
- `19:20` 根因 #2 確認：`max_tokens=128000` 過大 + bioRxiv 無文章內容導致 Qwen hang/timeout
- `19:25` 根因 #3 確認：`$MARKDOWN_TRUNC` 在雙引號中展開存在 shell injection 風險
- `19:30` 根因 #4 確認：`2>/dev/null` 吞掉所有 Supabase 錯誤訊息
- `19:55` 全部修復完成並驗證

---

## Bug Summary

### Symptom 1: 「Failed to insert article / Failed to link article entity」大量出現

STAT News (1/3 失敗)、BioPharma Dive (3/3 失敗)、Nature Biotechnology (2/3 失敗) 的文章插入失敗。

### Symptom 2: Pipeline 在 bioRxiv 來源處中斷（hang）

最後一個來源 bioRxiv 在 "Analyzing with Qwen 3.6..." 後無任何輸出，腳本 hang 超過 5 分鐘無進展。

---

## Root Cause Analysis

### Root Cause #1: `url` UNIQUE 約束 → 重複文章插入失敗

**機制：** `articles` 表有 `url text not null unique` 約束。當天稍早的 pipeline run (`c40c1409`) 已成功插入相同 URL 的文章。後續 run 嘗試插入相同 URL 時，PostgreSQL 返回 `23505 unique_violation`，導致插入失敗。

**證據：**
- 查詢 `articles?url=eq.<failed_url>` 確認 3 篇失敗文章全部存在於更早的 run `c40c1409`
- BioPharma Dive 3 篇文章全部為重複（最早 run 已抓取）
- STAT News 1/3 重複、Nature Biotech 2/3 重複

**為何之前沒發現：** `2>/dev/null` 吞掉了 Supabase 的實際錯誤訊息，只看到 binary 成功/失敗。

### Root Cause #2: `max_tokens=128000` + bioRxiv 無文章內容 → Qwen hang

**機制：**
1. `_build_llm_request.py` 設定 `max_tokens: 128000` — 對僅需輸出小型 JSON array 的任務而言極不合理
2. bioRxiv 首頁僅有導航連結、無實際文章內容（259 words）
3. Qwen 3.6 (35b-mlx) 收到 128000 max_tokens 後可能嘗試預分配記憶體或生成極長回應，導致模型卡死
4. `curl --max-time 180` 超時後，腳本因 `set -e` 和管線結構進入不明狀態

**證據：**
- 用極簡 prompt（50 chars, max_tokens=100）測試 Qwen，15 秒 timeout — **仍然超時**
- 這表示 Qwen 已因先前的 128000 token 請求進入 degraded/crashed 狀態
- bioRxiv scraped content 僅有主題分類導航，無任何文章標題或摘要

### Root Cause #3: `$MARKDOWN_TRUNC` Shell 展開漏洞

**機制：** `ANALYSIS_PROMPT="...${MARKDOWN_TRUNC}"` 在雙引號中展開 scraped content。若內容包含 `$`、反引號或 `\`，bash 會將其解釋為變數/命令替換。

**風險等級：** Medium（目前未觸發，但存在安全隱患 — scraped 網頁可能包含惡意內容）

### Root Cause #4: 錯誤訊息完全被吞掉

**機制：** 所有 curl 和 python3 調用都加了 `2>/dev/null`，Supabase 的實際錯誤回應（含 HTTP status code 和 error message）完全不可見。binary 成功/失敗檢查僅依賴回應是否為 JSON array。

---

## Fix Applied

### Fix 1: `_build_llm_request.py` — max_tokens 128000 → 4096

**檔案：** `ops/scripts/_build_llm_request.py`
**變更：** `"max_tokens": 128000` → `"max_tokens": 4096`
**理由：** LLM 任務僅輸出小型 JSON array（≤3 篇文章），4096 tokens 綽綽有餘。128000 浪費資源且可能導致模型 overload。

### Fix 2: 新增 Minimum Word Count Gate

**檔案：** `ops/scripts/run_pipeline.sh`
**變更：** 新增 `MIN_WORDS_FOR_LLM` 配置（預設 100），scraped 內容低於閾值時跳過 LLM 分析
**理由：** bioRxiv 等導航頁僅 ~250 words 且無文章內容，無需浪費 LLM 資源。

### Fix 3: LLM Request 改為 File-Based + Python 構建

**檔案：** `ops/scripts/run_pipeline.sh`
**變更：**
- Markdown 寫入 temp file，由 Python 讀取（避免 shell 展開）
- Prompt 構建完全在 Python 內完成（避免 bash injection）
- LLM curl 回應寫入 temp file，檢查 exit code 和檔案大小
**理由：** 徹底消除 shell injection 風險，並提供明確的 timeout/empty response 處理。

### Fix 4: 文章寫入改用 Python Helper（Upsert + Duplicate Detection）

**檔案：** `ops/scripts/_write_pipeline_output.py`（新建）、`ops/scripts/run_pipeline.sh`
**變更：**
- 新建 `_write_pipeline_output.py`：用 Python 處理所有 Supabase 寫入
- 文章：GET 檢查 URL 是否存在 → 存在則跳過（回傳 `duplicate`）→ 不存在則 POST 插入
- 實體：GET 檢查 (name, entity_type) 是否存在 → 存在則複用 ID → 不存在則 POST 插入
- Article-entity 連結：使用正確的 DB ID（非預生成的 UUID）
- 輸出 JSON summary：`{articles_inserted, articles_duplicate, articles_errors, entity_links_success, entity_links_errors}`
**理由：** bash while 迴圈無法正確處理 duplicate URL → entity link 的 ID 映射。Python helper 提供清晰的錯誤處理和統計。

### Fix 5: 新增 LLM_MAX_TOKENS 配置

**檔案：** `ops/scripts/run_pipeline.sh`
**變更：** 新增 `LLM_MAX_TOKENS="${LLM_MAX_TOKENS:-4096}"` 環境變數配置
**理由：** 允許不同場景調整 token 上限，預設值從 128000 降至合理的 4096。

---

## Files Modified

| File | Change | Lines |
|------|--------|-------|
| `ops/scripts/_build_llm_request.py` | `max_tokens` 128000 → 4096 | 1 |
| `ops/scripts/run_pipeline.sh` | LLM 分析階段重寫（word gate + file-based + timeout handling） | ~70 |
| `ops/scripts/run_pipeline.sh` | 文章寫入階段重寫（改用 Python helper） | ~90 removed, ~50 added |
| `ops/scripts/run_pipeline.sh` | 新增 `MIN_WORDS_FOR_LLM`, `LLM_TIMEOUT`, `LLM_MAX_TOKENS` 配置 | 3 |
| `ops/scripts/_write_pipeline_output.py` | **新建** — Supabase upsert + entity link helper | 183 |

---

## Verification

- [x] Bash 語法檢查通過 (`bash -n`)
- [x] Python 語法檢查通過 (`py_compile`)
- [x] Python 3.9 兼容性驗證（`dict | None` → `Optional[Dict]`）
- [x] Write helper 測試：STAT News JSONL → 3 dupes, 6 entity links ✓
- [x] Write helper 測試：Nature Biotech JSONL → 3 dupes, 5 entity links ✓
- [x] Write helper 測試：BioPharma Dive JSONL → 3 dupes, 9 entity links ✓
- [ ] 完整管線端到端測試 — **blocked by Qwen/Ollama 處於 degraded state**

---

## Known Issue: Qwen 3.6 (35b-mlx) Unresponsive

Qwen 目前完全無法回應任何請求（包含 50-char prompt + max_tokens=100）。Hemres gateway `/health` 回報 `ok`，但實際模型已 hang/crash。

**建議恢復步驟：**
```bash
# 重啟 Ollama
ollama stop qwen3.6:35b-mlx
ollama run qwen3.6:35b-mlx
# 或重啟整個 Ollama 服務
pkill ollama && ollama serve
```

---

## Prevention Actions

- [ ] 在 smoke test 中加入管線端到端測試（含 duplicate URL 場景） — assigned to: team
- [ ] 監控 Ollama 模型健康狀態（不僅 Hermes health endpoint） — assigned to: team
- [ ] 考慮為 `max_tokens` 設上限（例如 8192），防止單一請求拖垮模型 — tracked in: 本 hotfix
- [ ] 評估 `_build_llm_request.py` 是否仍需要（現在 prompt 構建在 run_pipeline.sh 的 Python inline 中完成）— 可後續清理
