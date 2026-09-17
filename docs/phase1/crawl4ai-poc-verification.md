# Crawl4AI PoC 實測驗證報告（P0）

## Document Status

| Field | Value |
| --- | --- |
| Status | Verification Report（P0 最小實測證據） |
| Date | 2026-09-18 |
| Reader | 決策者 / 工程師 / PM |
| 上層文檔 | `crawl4ai-migration-feasibility-review.md`、`crawl4ai-migration-engineering-spec.md`、`crawl4ai-migration-overview.md` |

## Executive Summary

B-4 環境重建完成（Python 3.12 venv + Crawl4AI **0.9.3** + Playwright Chromium），並對 **P0 未知數 1 —「Crawl4AI v0.9.x 新 API + Ollama qwen3.6:35b-mlx 能否端到端跑通 LLM extraction」** 完成最小實測：

- **✅ Markdown-only 爬蟲**：真實 bioRxiv preprint 頁 `status=200`、`word_count=2173`、`success=true`
- **✅ LLM extraction 端到端**：Ollama `qwen3.6:35b-mlx`（MLX engine，100% GPU，21GB）回傳**完整合法 JSON**（`title` / dense `summary` / `priority_level` / `entities[]` 含 company/drug/person/technology 全 type）
- 過程發現並修復 2 個 POC 的 v0.9.3 API 相容 bug（見 §5）

**結論：未知數 1 已回答（✅ 可端到端）** — Crawl4AI 0.9.3 + Ollama MLX LLM extraction 在 Mac Studio M3 Ultra 96GB 上跑通。相關量化發現（§4）：單篇 LLM extraction 首輪 ~9.5 分鐘（含 9352-token prompt 首次處理），warm 後 ~5.4 分鐘 — 對 P1 pipeline 的每篇延遲預算有重要參考價值。

## 1. 環境版本

| 元件 | 版本 | 備註 |
| --- | --- | --- |
| Python | 3.12.9 | `/opt/homebrew/bin/python3.12`（F-4 建議，避開 greenlet 3.13 issue #291） |
| venv | `.venv/` | repo 根；`.gitignore` 已加入 `.venv/` |
| pip | 26.2.1 | 升級自 venv 內建 |
| Crawl4AI | **0.9.3** | 與可行性 review 預期一致 |
| Playwright | 1.63.0 | Chromium Headless Shell 153.0.8010.12 |
| Trafilatura | 2.2.0 | |
| Pytest | 9.1.1 | |
| PyYAML | 6.0.3 | 既有相依 pin |
| Langfuse | 2.60.10 | 既有相依 pin |
| Ollama | 0.19+ | `qwen3.6:35b-mlx` 21GB，MLX engine 100% GPU |

環境驗收命令全數通過：
- `from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, LLMConfig, DefaultMarkdownGenerator, PruningContentFilter` → `OK`
- `import trafilatura` → `OK`
- `playwright install chromium` → 下載完成無報錯

## 2. 實測 URL 與選用說明

| 項目 | 值 |
| --- | --- |
| 任務指定 URL | `https://www.biorxiv.org/content/10.1101/2026.01.01.123456v1` |
| 實際採用 URL | `https://www.biorxiv.org/content/10.1101/2024.05.21.595135v1` |
| 說明 | 任務指定 URL 為**虛構 DOI**（`2026.01.01.123456` 不存在）：curl 回 429（Cloudflare bot 偵測），Playwright 實抓回 302 重導向至站台導覽頁（`word_count=653` 無文章正文）。改用 POC `DEFAULT_URLS` 內的**真實 preprint**（Norepinephrine Signals Through Astrocytes To Modulate Synapses）取得文章正文（`word_count=2173`），符合任務「若該 bioRxiv URL 404，改抓任一公開文章頁並標記」的指示 |

## 3. 實測結果

### 3.1 Markdown-only（不跑 LLM）

```bash
.venv/bin/python3 ops/poc/crawl4ai_poc.py --url https://www.biorxiv.org/content/10.1101/2024.05.21.595135v1
```

| 指標 | 值 |
| --- | --- |
| success | ✅ `true` |
| status_code | 200 |
| word_count | 2173 |
| fetch / scrape 時間 | 1.76s / 0.06s |
| markdown | 非空，含文章標題導覽 + 正文 |

（任務指定 URL 實測：`success=true`、`status=302`、`word_count=653` — 站台導覽列，因虛構 DOI 重導向。）

### 3.2 LLM extraction（Ollama qwen3.6:35b-mlx 端到端）

```bash
.venv/bin/python3 ops/poc/crawl4ai_poc.py --url https://www.biorxiv.org/content/10.1101/2024.05.21.595135v1 --llm
```

| 指標 | 值 |
| --- | --- |
| EXTRACT 時間（首輪） | **569.61s（~9.5 分鐘）** |
| EXTRACT 時間（warm 重跑） | ~5m24s（Ollama server.log：`POST /v1/completions took=5m23.9s status="200 OK"`） |
| 模型載入 | `qwen3.6:35b-mlx` 21GB → 22GB peak，MLX engine **100% GPU**，context 32768 |
| 回傳 JSON | ✅ 完整合法（見下方摘要） |

**extraction JSON 摘要**（節錄，完整內容見 log）：

```json
[
  {
    "title": "Norepinephrine Signals Through Astrocytes To Modulate Synapses",
    "summary": "This preprint reveals a novel mechanism by which norepinephrine (NE) modulates synaptic function... astrocytic pathways and adenosine A1 signaling as critical therapeutic targets...",
    "priority_level": "high",
    "entities": [
      { "name": "Norepinephrine", "entity_type": "drug" },
      { "name": "Adenosine A1 receptor", "entity_type": "technology" },
      { "name": "Katheryn B Lefton", "entity_type": "person" },
      { "name": "Thomas Papouin", "entity_type": "person" },
      { "name": "Washington University in St. Louis", "entity_type": "company" }
    ],
    "error": false
  },
  { "title": "...", "summary": "...", "priority_level": "medium", ... }
]
```

- **schema 欄位**：`title`、`summary`（dense，2 段式）、`priority_level`（high/medium 皆出現）、`entities[]`（company/drug/person/technology 四型齊全）— 與 POC `LLM_SCHEMA` 定義一致
- 模型會回傳**多個 JSON 物件**（同文章多次 extraction 結果），Crawl4AI 以陣列承接，格式正確

### 3.3 Ollama 延遲分解（對 P1 的啟示）

Ollama server.log 顯示首輪 prompt 處理 9352 tokens 耗時 ~9 分鐘（MLX engine 首載 + long prompt），warm 後 prefix cache 命中（`cached=9348/9352`），生成降到 ~5.4 分鐘。**對 P1 的意義**：單篇 LLM extraction 延遲遠高於 Firecrawl 雲端（秒級），需納入 pipeline budget；但這是本地 0 成本、資料不出機器換來的取捨。

## 4. 發現的問題與修復

| # | 問題 | 修復 |
| --- | --- | --- |
| P1 | `main_async` 引用 `args.use_llm`，但 argparse 定義的 flag 是 `--llm` → attribute 為 `args.llm`（`AttributeError: 'Namespace' object has no attribute 'use_llm'`） | `8b1b1c8`：`args.use_llm` → `args.llm`（2 處） |
| P2 | `CrawlerRunConfig(llm_config=...)` 是**不存在的參數**（v0.9.3 已移除；官方用法是 `LLMConfig` 只經 `LLMExtractionStrategy(llm_config=...)` 傳入）→ `TypeError: unexpected keyword argument 'llm_config'` | `8b1b1c8`：移除 `run_kwargs["llm_config"] = llm_config` 一行，`llm_config` 僅保留給 `LLMExtractionStrategy` |

> 註：P2 與可行性 review 的 B-1 判定一致 — spec/POC 的舊式參數問題真實存在，修復路徑即 review 建議的 `LLMConfig(provider=...)` + `markdown_generator=DefaultMarkdownGenerator(content_filter=PruningContentFilter(threshold=0.5))`（後者 POC 原本就正確）。

**CLI 差異標記**：任務描述假設 POC 有 `--no-llm` flag，實際 POC 以 `--llm` 開啟 LLM、**預設即 markdown-only**（讀 `ops/poc/crawl4ai_poc.py` argparse 確認）。未改 CLI 簽名（不屬於本任務 scope）。

## 5. 結論 — 未知數 1

> **✅ 已回答（可端到端）**：Crawl4AI **0.9.3**（新 API：`LLMConfig` + `DefaultMarkdownGenerator` + `PruningContentFilter` + `LLMExtractionStrategy(llm_config=...)`）+ Ollama **`qwen3.6:35b-mlx`**（MLX engine，100% GPU）在 Mac Studio M3 Ultra 96GB 上端到端跑通 LLM extraction，回傳符合 schema 的完整 JSON。

## 6. 附錄

### 6.1 操作指令

```bash
# 環境（一次性）
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install crawl4ai playwright trafilatura pytest PyYAML langfuse
playwright install chromium

# 實測
.venv/bin/python3 ops/poc/crawl4ai_poc.py --url <URL>            # markdown-only
.venv/bin/python3 ops/poc/crawl4ai_poc.py --url <URL> --llm      # LLM extraction
```

### 6.2 Commits

| Hash | Message |
| --- | --- |
| `9ecd885` | `chore(dev): add crawl4ai/playwright/trafilatura/pytest to requirements-dev.txt`（+ `.gitignore` 加 `.venv/`） |
| `8b1b1c8` | `fix(poc): align crawl4ai_poc with v0.9.3 API and CLI` |
| （待本檔） | `docs: add Crawl4AI PoC verification results (P0)` |

### 6.3 已知限制

- 單一 URL 實測（bioRxiv preprint）— 未涵蓋 STAT News / Fierce Biotech 等 Cloudflare 高風險源（屬 P1 或後續 PoC scope）
- LLM extraction 僅驗證「回傳合法 JSON + schema 欄位齊全」，未做欄位值品質評分
- 首次 LLM extraction 需 ~9.5 分鐘（含模型載入 + long prompt 首次處理）；warm 後 ~5.4 分鐘