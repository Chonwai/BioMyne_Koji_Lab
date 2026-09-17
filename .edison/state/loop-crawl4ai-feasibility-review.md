# Loop State: Crawl4AI 遷移可行性調查

Goal: 深入調查兩份文檔（overview + engineering-spec）內容合理性，並評估「遷移至本地 Playwright + Crawl4AI + Ollama」是否真的能成功順利達成（≥95% 抓取成功率、content_hash 去重維穩、LLM 覆蓋率不降、成本 $16→~$4.32、3 hard sources 保留 Cloud fallback）。產出可行性調查報告（證據導向），達 strict 93 閘門。hackathon 式多 commit。
Started: 2026-09-18
Status: active
Quality Mode: strict (93)
Depth Level: L3 Deep Dive
Snapshot Cache: /Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji/docs/.project-context.md (STALE)
Snapshot Evidence Status: LOCATOR-ONLY — 快取僅供定位，Critical findings 必須實時 scan 驗證
Budget: ~14 iterations

## Stage Round Counters（v4.3）

| Stage | Current Round | Max Rounds | Status |
| --- | :---: | :---: | --- |
| DISCOVER（雙軌：codebase 驗證 + 外部深研） | 1 | 2 | ✅ done（見 Iteration 1） |
| PLAN（可行性報告撰寫） | 0 | 2 | pending |
| VERIFY（smith doc-review strict 93） | 0 | 3 | pending |
| REPAIR（trinity bounded） | 0 | 2 | pending |

## 任務形態分類

- 類型：Research + Plan（Loop B+）→ DISCOVER → PLAN → VERIFY → ITERATE
- 混合調度：R4 跨部門外借（研究部 morpheus + jarvis-deep-research；規劃部 architect；品管部 smith）
- Maker ≠ Checker：DISCOVER/PLAN（morpheus / jarvis-deep-research / architect）≠ VERIFY（smith）✓

## Iterations

### Iteration 1 — DISCOVER（雙軌並行，2026-09-18）

**Track 1: morpheus（codebase 實測）** — 25 項 claim 逐項驗證：
- ✅ 吻合：所有程式錨點（L225/L583/L618/L1103、scrape L80–88、credit L19–25、smoke L94）100% 存在；manifest 11 來源 8/3 分類與 spec §2.2 逐列一致；`qwen3.6:35b-mlx` 21GB 已實裝；Paywall 相容就緒；memo cost tool $16/660 吻合
- ✗ 不符：`run_pipeline.sh:258` select 僅 10 欄**無 crawler_provider**；三層 provider 決策（CRAWLER_ALLOW_CLOUD/DB/env）**完全未實作**；環境空轉（無 venv，requirements-dev.txt 僅 2 套件，連 PyYAML 都沒裝）
- ⚠️ 部分：MN_WORDS_FOR_LLM 三處不一致（code 100 / .env.example 100 / live .env=300）；retry 命名 FIRECRAWL_SCRAPE_ATTEMPTS 非 MAX_ATTEMPTS
- 🟠 中：hash_markdown() 僅文字層 normalize（NFC/comment/空白/lowercase），抗不了時間戳/廣告/動態內容

**Track 2: jarvis-deep-research（外部深研，Exa 4 輪 + 一手來源）** — T1–T6：
- ✅ **三大支柱全真實**：Crawl4AI v0.9.3（2026-08-31 安全 release，活躍）；`qwen3.6:35b-mlx` 官方 library 真實存在（24GB MoE，Ollama 0.19+ Apple Silicon 原生 MLX backend，M3 Ultra 96GB 綽綽有餘）；Firecrawl 定價正確（$16 年繳/$19 月繳/5000 credits/Free 1000，2026-09-04 生效）
- 🔴 **高：Crawl4AI API 已改版** — spec/POC 用的 `LLMExtractionStrategy(provider=...)`、`markdown=True`、`only_main_content=True` 是舊式（Firecrawl 風格）參數，v0.9.x 已棄用，需 `LLMConfig(provider=...)` + `markdown_generator=DefaultMarkdownGenerator(content_filter=PruningContentFilter(...))`。照 spec 實作第一道卡點
- 🔴 **高：95% 成功率目標偏樂觀** — Crawl4AI 業界平均 ~89.7%（datacelix 2026-07-07）；20 runs ≤1 fail 需每 source 真實成功率 ≥97.5%（0.975^20≈0.6）
- 🟡 中高：**STAT News（Cloudflare + Boston Globe Media 封鎖所有 bots + tinypass paywall）與 Fierce Biotech（Cloudflare）在 8 個 easy sources 中風險最高**
- 🟡 中：content_hash 穩定性（多來源實證：廣告/timestamp/推薦區塊會弄壞 hash；需 normalize + 只 hash 主文區）
- stealth ~5%/~70% 數據有出處但為 vendor benchmark（humanbrowser 2026-02-19），且 ~5% 實為「VPS IP + stealth」組合結果

**雙軌交叉結論**：遷移「技術上可行、方向正確、主要假設真實」；但「順利達成」取決於 3 個未驗證未知數（① API 端到端跑通 ② 8 sources 真實反爬現況 ③ 模型 tag 已交叉確認 21GB）。風險在「實作細節過時」與「目標偏樂觀」，非架構錯誤。

**Outcome: DISCOVER ✅ → dispatch architect（PLAN）**

## Circuit Breaker

Consecutive fails: 0/3
Budget: 15%
Status: HEALTHY