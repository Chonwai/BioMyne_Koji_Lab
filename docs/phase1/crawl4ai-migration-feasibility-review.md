# Crawl4AI 本地爬蟲棧遷移 — 可行性調查報告

## Document Status

| Field | Value |
| --- | --- |
| Status | Feasibility Review（調查報告，非權威文檔） |
| Date | 2026-09-18 |
| Reader | 決策者 / 工程師 / PM |
| Quality target | 93+（strict） |
| 上層文檔 | `crawl4ai-migration-overview.md`（v1.1）、`crawl4ai-migration-engineering-spec.md` |

## Executive Summary

兩份文檔（overview + engineering-spec）的核心宣稱經雙軌調查（codebase 實測 25 項 claim + 外部多源深研 6 主題）驗證：**文檔藍圖真實、方向正確，三大技術支柱（Crawl4AI v0.9.3、Ollama Qwen3.6-35B-A3B-mlx、Firecrawl 定價）全部成立**。但調查發現：① spec/POC 使用的 Crawl4AI API 是已棄用的舊式參數（`LLMExtractionStrategy(provider=...)`），照 spec 實作第一道就卡；② 「8 sources ≥95% 成功率」目標偏樂觀（Crawl4AI 業界平均 ~89.7%）；③ 遷移 Step 4 的 provider routing 在目前 codebase **完全未實作**（select 僅 10 欄、三層決策不存在、sql/006 不存在、環境空轉）。結論：**遷移可行且值得做，但「順利達成」取決於先解決 3 個 P0 未知數 + 4 個 BLOCKING 缺口；95% 目標需下修為「平均 ≥95%、單一 source ≥80%」並預留 per-domain 調校預算。**

## 1. 調查方法

- **Track 1 — codebase 實測（morpheus）**：對文檔中 25 項技術 claim 逐項實測（檔案存在性、行號、DDL、依賴、環境、manifest 分類），100% 只讀
- **Track 2 — 外部深研（jarvis-deep-research）**：6 主題（Crawl4AI 能力 / Qwen 模型真實性 / 反爬現況 / Trafilatura / Firecrawl 定價 / 成功率基準），每項至少 2 個獨立來源交叉驗證（Exa 4 輪 + 一手來源 GitHub/官方文件）
- 證據等級：實測（檔案:行號）/ 一手來源（官方 docs/GitHub）/ 二手（benchmark/vendor）

## 2. 文檔合理性評比

### 2.1 Overview — ✅ 整體合理（4 處需限定措辭，前 loop 已修）

| 節 | 判定 | 證據 |
| --- | --- | --- |
| Executive Summary（$16→$4.32、8/11、2–3 週） | ✅ 合理 | cost tool 參數 $16/660 吻合；manifest 8/3 分類一致 |
| §1 驅動力（成本/隱私/彈性） | ✅ 合理 | 電費 30W×24h×30d×$0.2 ≈ $4.32 數學正確 |
| §2 遷移前後對比 | ✅ 合理（有限定註記） | 前 loop R3 已加「8 個遷移來源限定」 |
| §4 風險（P1 反爬 5%→70%） | ⚠️ 數字有出處但需註明 vendor benchmark | humanbrowser 2026-02-19，且 ~5% 實為「VPS IP + stealth」 |
| §6 成功指標（≥95%） | ⚠️ 偏樂觀 | 業界 Crawl4AI ~89.7%；見 §5 |
| §7 決策建議 | ✅ 合理 | 保留 Cloud fallback + Free tier 是最務實路線 |

### 2.2 Engineering Spec — ⚠️ 大方向正確，但 3 處需修正（1 blocking）

| 節 | 判定 | 證據 |
| --- | --- | --- |
| §3 關鍵設計決策（LLMExtractionStrategy provider=ollama/qwen3.6:35b-mlx） | 🔴 **有誤（blocking）** | v0.9.x 已棄用 direct provider；需 `LLMConfig(provider=...)`（官方 #1163/#1770） |
| §4.1 CrawlerProvider 介面 | ✅ 合理 | 抽象介面設計正確，Firecrawl 包 asyncio.to_thread 正確 |
| §4.2 LocalCrawl4AIProvider（markdown=True, only_main_content=True） | 🔴 **有誤（blocking）** | 舊式參數；需 `markdown_generator=DefaultMarkdownGenerator(content_filter=PruningContentFilter(...))` |
| §4.3 切換機制（三層優先序） | ✅ 設計合理（未實作） | codebase 實測：三層決策完全不存在，屬「待實作」 |
| Step 4 source-level routing（select 11 欄） | ⚠️ 目標規格非現況 | `run_pipeline.sh:258` 現況 10 欄無 crawler_provider |
| Step 5 AC（content_hash 穩定率 ≥80%） | ✅ 合理（可達成） | hash_markdown() 存在但僅文字層 normalize（見 §6 NB-2） |
| AC-1（≥95%, 20 runs ≤1 fail） | 🔴 **偏樂觀** | 需每 source ≥97.5%（0.975^20≈0.6）；建議下修 |
| §9 風險表（反爬/飄移/版本/Ollama/Playwright） | ✅ 完整合理 | 五項風險均有對應 rollback |

### 2.3 POC 檔（crawl4ai_poc.py）

| 判定 | 證據 |
| --- | --- |
| 🔴 舊式 API（L95–110 LLMExtractionStrategy provider=） | 與 spec 同源問題；P0 第一件事改寫 |

## 3. 遷移成敗證據判斷

**三大支柱（全部 ✅ 真實）：**

| 支柱 | 驗證結果 | 證據 |
| --- | --- | --- |
| Crawl4AI v0.9.3 | 最新穩定版（2026-08-31 安全 release，5 CVE+33 fixes），專案活躍 | GitHub CHANGELOG/README |
| Ollama Qwen3.6-35B-A3B-mlx | 官方 library 真實存在（24GB MoE，2026-04-16）；Ollama 0.19+ Apple Silicon 原生 MLX；M3 Ultra 96GB 綽綽有餘（M1 Ultra 實測 45–66 tok/s） | ollama.com/library + omlx.ai benchmark + `ollama list` 實測 21GB 已安裝 |
| Firecrawl 定價 | $16 年繳/$19 月繳/5000 credits/Free 1000/map 1 credit（2026-09-04 生效）；公司健康（Series A $14.5M） | firecrawl.dev/pricing + TechCrunch |

**成功率目標 vs 業界基準：**

| 指標 | 文檔宣稱 | 業界實測 | 落差 |
| --- | --- | --- | --- |
| Crawl4AI 平均 success rate | ≥95%（AC-1） | ~89.7%（datacelix 2026-07-07） | ~5 點 |
| anti-bot 目標 | — | Crawl4AI ~72% / Firecrawl ~88.4% | 需 per-domain 調校 |
| markdown quality Recall@5 | — | Crawl4AI 84.5% / Firecrawl 89.0%（spider.cloud 2026-02-11） | 4.5 點（可調校縮小） |

## 4. 缺口清單

### 🔴 BLOCKING（4 項 — 不做則遷移無法落地）

| # | 缺口 | 現況 vs 需求 | 影響 | 修復成本 |
| --- | --- | --- | --- | --- |
| B-1 | Crawl4AI API 版本落差 | spec/POC 用舊式參數 vs v0.9.x 新 API（LLMConfig + content_filter + markdown_generator） | 照 spec 實作即卡（KeyError: 'provider' / deprecation） | 低（改 code snippet，0.5–1 hr） |
| B-2 | provider routing 未實作 | `run_pipeline.sh:258` select 10 欄無 crawler_provider；三層決策（CRAWLER_ALLOW_CLOUD→DB→env）全缺 | Step 4 核心依賴不存在，無法 source-level 切換 | 中（改 shell + 新增 sql/006，2–4 hr） |
| B-3 | sql/006 與 DB 欄位不存在 | `sources` 表無 crawler_provider；sql/006 檔不存在 | 無 DB 層 routing 依據 | 低（新增 migration，0.5 hr） |
| B-4 | 執行環境空轉 | 無 venv；requirements-dev.txt 僅 2 行；crawl4ai/playwright/trafilatura 全未安裝 | 任何實作都無法跑 | 低（建 venv + pip install + playwright install，1–2 hr） |

### 🟡 NON-BLOCKING（5 項 — 影響品質/效率，不阻斷）

| # | 缺口 | 說明 | 建議 |
| --- | --- | --- | --- |
| NB-1 | 95% 目標過高 | 業界 ~89.7%；20 runs ≤1 fail 需 ≥97.5%/source | 下修 AC-1 為「8 sources 平均 ≥95%、單一 ≥80%」 |
| NB-2 | hash_markdown() 僅文字層 normalize | 抗不了時間戳/廣告/動態內容（naman.so 實證 127 次 refetch） | hash 前 strip 易變區塊；只 hash fit_markdown 主文 |
| NB-3 | MIN_WORDS_FOR_LLM 三處不一致 | code 100 / .env.example 100 / live .env 300 | 統一並在驗收測試用 live 值 |
| NB-4 | STAT News / Fierce Biotech 在 Cloudflare 後 | STAT 母公司封鎖所有 bots + tinypass paywall | P0 實測；若全文抓取失敗率高，移入 hard sources（3→4） |
| NB-5 | stealth 數據未註明 vendor benchmark | humanbrowser 2026-02-19（利益相關）；~5% 實為 VPS IP + stealth | overview §4 加註來源與語境 |

## 5. P0 PoC 前必須回答的未知數

1. **Crawl4AI v0.9.3 新 API（LLMConfig/content_filter）+ Python 3.12 + Ollama qwen3.6:35b-mlx 能否端到端跑通 LLM extraction？**（用 Python 3.12 避 greenlet 相容；M3 Ultra 上先跑最小驗證）
2. **8 個 easy sources 各自的真實反爬現況？**（STAT/Fierce 已知 Cloudflare；逐一實測 RSS vs 全文 vs 被擋比例；STAT 全文失敗率過高就移入 hard）
3. **Ollama MLX backend 版本確認**（≥0.19 才有原生 MLX；<0.19 會 fallback Metal，效能打折）

## 6. 對 spec/overview 的修正建議清單（供後續 loop 執行）

| # | 檔案 | 位置 | 修正 |
| --- | --- | --- | --- |
| F-1 | spec | §3 關鍵設計決策 + §4.2 + Step 3 | `LLMExtractionStrategy(provider=...)` → `CrawlerRunConfig(markdown_generator=DefaultMarkdownGenerator(content_filter=PruningContentFilter(threshold=0.5)))` + `llm_config=LLMConfig(provider="ollama/qwen3.6:35b-mlx")` |
| F-2 | spec | AC-1 / Step 5 驗收 | 「8 sources ≥95%」→「8 sources 平均 ≥95%、單一 source ≥80%」+ 註明需 per-domain 調校 |
| F-3 | spec | Step 4 | 補註「select 11 欄為目標狀態；現況 run_pipeline.sh:258 為 10 欄，需實作」 |
| F-4 | spec | §9 / Step 1 | 加 Python 3.12 建議（greenlet 相容）與 `DYLD_LIBRARY_PATH` 注意事項 |
| F-5 | overview | §4 P1 | stealth ~5%/~70% 加註「vendor benchmark（humanbrowser 2026-02-19）；~5% 為 VPS IP + stealth 組合結果」 |
| F-6 | spec | Step 5 content_hash AC | 加「hash 前 normalize + 只 hash 主文區（fit_markdown）」建議 |

## 7. 結論與建議

**文檔合理嗎？** 大方向合理、藍圖真實（所有程式錨點與分類經實測吻合）；但有 1 個 blocking API 錯誤（舊式參數）與 1 個偏樂觀目標（95%）。

**遷移能成功嗎？** 能——三大支柱全真實、架構正確、風險可控。但「順利達成」取決於：先解決 B-1..B-4（API 修正 + routing 實作 + DB migration + 環境重建），再以 P0 回答 3 個未知數，並把 95% 目標下修。

**建議順序**：① 修 spec/POC API 錯誤（B-1）→ ② 建環境跑 P0 最小驗證（B-4 + 未知數 1）→ ③ 逐一實測 8 sources 反爬（未知數 2）→ ④ 實作 sql/006 + run_pipeline.sh routing（B-2/B-3）→ ⑤ P2 遷移與驗收。任何 source 抓取成功率 <80% 即依文檔回滾閘切回 Firecrawl。

## 附錄：證據索引

| 來源 | URL | 日期 | 用途 |
| --- | --- | --- | --- |
| Crawl4AI CHANGELOG | github.com/unclecode/crawl4ai/blob/main/CHANGELOG.md | 2026-08-31 | v0.9.3 版本確認 |
| Crawl4AI Issue #1163 | github.com/unclecode/crawl4ai/issues/1163 | 2025-05-28 | provider 應放 LLMConfig |
| Crawl4AI Issue #1770 | github.com/unclecode/crawl4ai/issues/1770 | 存取 2026-09-18 | 棄用 API modernize |
| Ollama library qwen3.6:35b-mlx | ollama.com/library/qwen3.6:35b-mlx | 2026-09 初更新 | 模型真實性 |
| Ollama MLX blog | ollama.com/blog/mlx | 2026-03-30 | Apple Silicon MLX backend |
| oMLX benchmark | omlx.ai/benchmarks/yxrq14l8 | 2026-05-27 | M1 Ultra 45–66 tok/s |
| datacelix benchmark | datacelix.com/crawl4ai-vs-firecrawl/ | 2026-07-07 | success rate 89.7% vs 95.3% |
| spider.cloud benchmark | spider.cloud/blog/firecrawl-vs-crawl4ai-vs-spider-honest-benchmark/ | 2026-02-11 | markdown recall 84.5% vs 89% |
| humanbrowser benchmark | humanbrowser.cloud/blog/bypass-cloudflare-playwright-2026 | 2026-02-19 | stealth 5%/~70% 出處 |
| newsmediahelpdesk | newsmediahelpdesk.org/ai-visibility-news-publishing-strategy/ | 2026-08-24 | STAT 母公司封鎖 bots |
| naman.so simhash | naman.so/blog/simhash-web-crawl-caching | 2025-10-07 | ad rotation 127 refetch |
| Firecrawl pricing | firecrawl.dev/pricing | 2026-09-04 | 定價驗證 |
| Trafilatura v2.2.0 | github.com/adbar/trafilatura/releases/tag/v2.2.0 | 2026-07-31 | 補強工具 |
| codebase 實測 | run_pipeline.sh:258 / sql/001 DDL / requirements-dev.txt / ollama list | 2026-09-18 | 缺口 B-2..B-4 |