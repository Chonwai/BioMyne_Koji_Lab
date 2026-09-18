# Loop State: Crawl4AI 遷移 P1 — Provider Abstraction

Goal: 正式啟動 P1 Provider Abstraction（spec §4/§5/Step 2–3 定義）：新增 `ops/scripts/crawler_providers.py`（CrawlerProvider Protocol + ScrapeResult + create_provider + FirecrawlProvider + LocalCrawl4AIProvider），將 `_scrape_markdown.py` 抽為 wrapper、`_discover_article_urls.py` firecrawl_map 走 provider.map、`_fetch_firecrawl_credit_usage.py` 條件化、`smoke_test.sh` 本地 health check、`ops/tests` pytest。達 strict 93 閘門。hackathon 式多 commit。
Started: 2026-09-18
Status: active
Quality Mode: strict (93)
Depth Level: L3 Deep Dive
Snapshot Cache: /Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji/docs/.project-context.md (STALE)
Snapshot Evidence Status: LOCATOR-ONLY — 快取僅供定位，Critical findings 必須實時 scan 驗證
Budget: ~18 iterations

## 硬體澄清（用戶 2026-09-18 提供）

- 9.5min LLM extraction 延遲為 **MacBook Pro 開發機**數據（非公司主機）
- 公司主機 = **Mac Studio M5 Ultra 96GB**（用戶提供；repo 記憶原為 M3 Ultra 已更新）— 快很多倍 → **速度疑慮解除，P1 正式啟動**
- P1 設計仍納入並行/延遲預算考量（不因硬體快而忽略）

## Stage Round Counters（v4.3）

| Stage | Current Round | Max Rounds | Status |
| --- | :---: | :---: | --- |
| DISCOVER（目標檔案現況確認） | 1 | 1 | ✅ done（Neo 直接讀 3 關鍵檔案） |
| PLAN（P1 實作 blueprint） | 0 | 1 | ➖ skipped（spec §4/§5 已定義，避免 over-planning） |
| EXECUTE（trinity 分步） | 0 | 3 | 🔄 active |
| VERIFY（smith strict 93） | 0 | 3 | pending |
| REPAIR（trinity bounded） | 0 | 2 | pending |

## 任務形態與範圍

- Loop C（Full Dev）— DISCOVER → PLAN → EXECUTE → VERIFY；Maker ≠ Checker ✓
- **範圍**（spec §1.2/§5）：crawler_providers.py 新增；_scrape_markdown.py 抽 wrapper（JSON 輸出不變）；_discover_article_urls.py firecrawl_map → provider.map；_fetch_firecrawl_credit_usage.py 條件化；smoke_test.sh step 4 本地 health check；run_pipeline.sh SCRAPE_JSON 呼叫點接 provider；ops/tests pytest
- **Out of Scope**：GraphDB/dashboard/Hermes/residential proxy/schema 自動生成/Firecrawl SDK 移除（spec §1.3）
- 反爬實測（未知數 2）不阻斷 P1（影響 DB 值非介面架構）→ P2 前處理

## Iterations

### Iteration 1 — DISCOVER（Neo 直接掃描）

讀 3 關鍵檔案確認 P1 接線點：
- `_scrape_markdown.py`：Firecrawl 呼叫 L79–112 確認；輸出 JSON 含 `firecrawl_timeout_ms`（spec §4.4 7 欄相容，但 ScrapeResult dataclass 需決定是否保留此欄）
- `run_pipeline.sh`：provider routing 已在 L302–308（上輪 B-2），但 `PROVIDER` 變數**尚未接入** discovery/scrape 呼叫（P1 接線點）
- `_discover_article_urls.py`：`firecrawl_map()` L225–269 確認（map 回傳 list[dict]）
- **決定：跳過 architect blueprint**（spec §4/§5 已定義介面與檔案清單；避免 over-planning）→ 直接 trinity 分步 EXECUTE

**Outcome: DISCOVER ✅ → EXECUTE（trinity 分步，每步小 commit）**

## Circuit Breaker

Consecutive fails: 0/3
Budget: 5%
Status: HEALTHY