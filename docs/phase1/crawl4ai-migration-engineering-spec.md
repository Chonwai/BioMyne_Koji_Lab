# Crawl4AI 本地爬蟲棧遷移 — Engineering Handoff Spec

## Document Status

| Field                   | Value                                          |
| ----------------------- | ---------------------------------------------- |
| Status                  | Draft for Engineering Handoff                  |
| Phase                   | Phase 1 — Crawl4AI Migration                  |
| Intended reader         | Full-stack engineer                            |
| Baseline quality target | 93+                                            |
| Last updated            | 2026-09-17                                     |

---

## 1. Purpose & Scope Lock

### 1.1 目標

本 spec 定義 BioMyne Koji 爬蟲棧從 Firecrawl Cloud 遷移至本地 Playwright + Crawl4AI + Ollama 的完整工程規格。工程師可直接照著做，不需要回問 PM。

### 1.2 In Scope

1. **Provider Abstraction**：定義 `CrawlerProvider` 介面，讓 Firecrawl 與 Crawl4AI 可切換
2. **遷移 8 個 easy sources** 至本地 provider
3. **保留 3 個 hard sources** 的 Firecrawl Cloud fallback
4. **更新 `run_pipeline.sh`** 支援 source-level routing
5. **更新 smoke_test.sh** 本地 health check
6. **更新 source manifest** 加 `crawler_provider` 欄位

### 1.3 Out of Scope

- ❌ 不做 GraphDB / Neo4j 整合
- ❌ 不做 dashboard 改造
- ❌ 不碰 Hermes orchestration 層
- ❌ 不做 AI extraction schema 自動生成（Crawl4AI roadmap item）
- ❌ 不做 residential proxy 整合（反爬升級留待後續）
- ❌ 不移除 Firecrawl SDK 依賴（只抽 abstraction，不删舊 path）

---

## 2. 背景與現況

### 2.1 Firecrawl 4 端點使用位置

| # | 端點 | 檔案 / 行號 | 用途 | 遷移對應 |
| --- | --- | --- | --- | --- |
| 1 | `POST /v2/map` | `ops/scripts/_discover_article_urls.py` L225–269（`firecrawl_map()`）＋ L1103 呼叫點 | URL map 發現候選文章連結 | `feedparser`（RSS）優先，Crawl4AI sitemap/link 萃取補足 |
| 2 | `POST /v1/scrape` | `ops/scripts/_scrape_markdown.py` L79–112 | 單頁抓取 → markdown（`onlyMainContent`、`waitFor`、paywall markers） | Crawl4AI `AsyncWebCrawler` markdown extraction |
| 3 | `GET /v1/team/credit-usage` | `ops/scripts/_fetch_firecrawl_credit_usage.py`（全檔） | 觀測剩餘額度 | 改由 cost 估算工具替代 |
| 4 | `POST /v1/scrape`（health check） | `ops/scripts/smoke_test.sh` L94–114 | smoke test 驗證爬蟲可用 | 改為本地 Playwright/Crawl4AI self-check |

> **注意**：`_discover_article_urls.py` 中 RSS（`feed_candidates` L583）與 sitemap（`sitemap_candidates` L618）已為本地原生存取，**只有 map surface 走 Firecrawl**。遷移後 Firecrawl 僅剩 Endpoints/BioCentury/Science 的 map/scrape 路徑。

### 2.2 Source Manifest 現況（`ops/source-manifests/biotech.yaml`）

| Source | primary_discovery_surface | fallback_discovery_surface | 遷移類別 |
| --- | --- | --- | --- |
| STAT News | rss | map | ✅ Easy |
| BioPharma Dive | rss | map | ✅ Easy |
| Nature Biotechnology | sitemap | map | ✅ Easy |
| arXiv Quantitative Biology | rss | map | ✅ Easy |
| bioRxiv | category_page | map | ✅ Easy |
| Fierce Biotech | rss | map | ✅ Easy |
| GEN – Genetic Engineering & Biotechnology News | rss | map | ✅ Easy |
| SynBioBeta | category_page | map | ✅ Easy |
| **Endpoints News** | **map** | map | ⚠️ Hard（保留 Cloud） |
| **BioCentury** | rss | map | ⚠️ Hard（保留 Cloud） |
| **Science** | rss | map | ⚠️ Hard（保留 Cloud） |

---

## 3. 目標架構

```mermaid
flowchart LR
    subgraph Discovery["Discovery（本地）"]
        A[feedparser RSS] --> D
        B[sitemap XML] --> D
        C[Crawl4AI link/map 萃取] --> D
        D[URL 正規化 + 去重] --> E
    end

    subgraph Extraction["Extraction（本地）"]
        E{Provider Router} -->|easy sources| F[Crawl4AI AsyncWebCrawler]
        E -->|hard sources| G[Firecrawl Cloud Fallback]
        F --> H{品質閘門}
        G --> H
        H -->|不足| I[Trafilatura 補強全文]
        H -->|OK| J
        I --> J[hash_markdown + paywall 偵測]
    end

    J --> K{LLM 摘要}
    K --> L[Ollama Qwen 3.6<br/>LLMExtractionStrategy]
    L --> M[(Supabase + pgvector)]

    subgraph AntiBot["Anti-bot（僅需要時）"]
        N[stealth 插件] --> F
        O[residential proxy] -.-> F
    end
```

**關鍵設計決策**：
- Discovery 以 feedparser + sitemap 為主體（9/11 來源已是 RSS/sitemap 先行）
- Extraction 以 Crawl4AI 為主，Firecrawl 保留給 3 個 hard sources
- LLM 用 Ollama Qwen 3.6（`LLMExtractionStrategy(provider="ollama/qwen3.6:35b-mlx")`）
- Anti-bot 只在需要時啟用（stealth/residential proxy 都不是預設值）

---

## 4. Provider Abstraction 設計（P1 核心）

### 4.1 `CrawlerProvider` 介面

新增 `ops/scripts/crawler_providers.py`，定義抽象介面：

```python
class CrawlerProvider(Protocol):
    """Abstract interface for web scraping providers."""

    def scrape(self, url: str) -> ScrapeResult:
        """Scrape a single URL and return structured result.
        
        Returns ScrapeResult with fields:
        - success: bool
        - markdown: str
        - word_count: int
        - content_hash: str (from _pipeline_normalization.hash_markdown)
        - paywall_detected: bool
        - paywall_signal: str | None
        - provider: str ("firecrawl" | "crawl4ai" | "local")
        """
        ...

    def map(self, url: str, *, search: str | None = None, limit: int = 50) -> list[dict]:
        """Discover candidate article URLs from a given page/sitemap.
        
        Returns list of dicts with:
        - url: str
        - title: str (if available)
        - source: str (provider name)
        """
        ...
```

### 4.2 兩個實作

#### `FirecrawlProvider`

- 沿用現有 `_scrape_markdown.py` 邏輯（L79–112）
- 需要 `FIRECRAWL_KEY` 環境變數
- `map()` 呼叫 `firecrawl_map()` 邏輯（`_discover_article_urls.py` L225–269）
- 輸出 JSON 欄位保持不變

#### `LocalCrawl4AIProvider`

- 使用 `crawl4ai.AsyncWebCrawler`（參考 `ops/poc/crawl4ai_poc.py` L80–110）
- `scrape()` 設定：`headless=True`, `markdown=True`, `only_main_content=True`, `cache_mode=BYPASS`
- `map()` 使用 Crawl4AI 的 link discovery 或 sitemap XML 解析
- 需要 `pip install crawl4ai playwright && playwright install chromium`

### 4.3 切換機制

**雙層切換**：

1. **全域預設**：環境變數 `CRAWLER_PROVIDER=local|firecrawl`（預設 `local`）
2. **Source-level override**：`biotech.yaml` 每個 source 可加 `crawler_provider: firecrawl` 欄位

```yaml
# 範例：Endpoints News 保留 Firecrawl
- name: Endpoints News
  url: https://endpoints.news/
  crawler_provider: firecrawl  # source-level override
  ...

# 範例：STAT News 用本地（可省略，因為全域預設是 local）
- name: STAT News
  url: https://www.statnews.com/
  # crawler_provider: local  # 省略 = 用全域預設
  ...
```

### 4.4 相容性要求

**兩個 provider 輸出 JSON 欄位必須相容**：

| 欄位 | 類型 | 必須 | 說明 |
| --- | --- | --- | --- |
| `success` | `bool` | ✅ | 是否成功抓取 |
| `markdown` | `str` | ✅ | 抓取到的 markdown 內容 |
| `word_count` | `int` | ✅ | markdown 字數 |
| `content_hash` | `str` | ✅ | `hash_markdown()` 產生的雜湊 |
| `paywall_detected` | `bool` | ✅ | 是否偵測到 paywall |
| `paywall_signal` | `str \| None` | ✅ | paywall 類型標記 |
| `provider` | `str` | ✅ | 使用的 provider 名稱 |

`run_pipeline.sh` 只需將 `SCRAPE_JSON` 的解析邏輯從呼叫 `_scrape_markdown.py` 改為呼叫 `crawler_providers.py` 的對應方法，其他不動。

---

## 5. 要改的檔案清單

| 檔案 | 改動 | 為什麼 | 風險 |
| --- | --- | --- | --- |
| `ops/scripts/crawler_providers.py` | **新增** — `CrawlerProvider` 介面 + `FirecrawlProvider` + `LocalCrawl4AIProvider` | Provider abstraction 核心 | 低（新增檔案，不影響現有） |
| `ops/scripts/_scrape_markdown.py` | **改** — 抽出 scrape 邏輯到 `FirecrawlProvider`，保留為 wrapper | 讓 pipeline 可呼叫 provider | 中（需確保 JSON 輸出不變） |
| `ops/scripts/_discover_article_urls.py` | **改** — `firecrawl_map()` 改為呼叫 `provider.map()` | 讓 map 邏輯走 provider | 中（map 輸出格式需相容） |
| `ops/scripts/_fetch_firecrawl_credit_usage.py` | **改** — 加條件：`CRAWLER_PROVIDER=local` 時跳過 Firecrawl API call | 本地模式不需要 credit 觀測 | 低（不影響 Firecrawl 模式） |
| `ops/scripts/run_pipeline.sh` | **改** — 環境變數、fallback routing、source-level provider 決策 | 讓 pipeline 支援雙 provider | 中（shell 邏輯變動需測試） |
| `ops/scripts/smoke_test.sh` | **改** — step 4 改為本地 Crawl4AI health check | 本地模式不需要 Firecrawl API | 低（獨立測試腳本） |
| `ops/source-manifests/biotech.yaml` | **改** — 3 個 hard sources 加 `crawler_provider: firecrawl` | source-level routing | 低（YAML 欄位新增） |

---

## 6. 遷移步驟（Step-by-Step）

### Step 1: 環境準備

**指令**：
```bash
pip install crawl4ai playwright trafilatura
playwright install chromium
```

**驗收標準**：
- [ ] `python3 -c "from crawl4ai import AsyncWebCrawler; print('OK')"` 輸出 OK
- [ ] `playwright install chromium` 無報錯
- [ ] `python3 -c "import trafilatura; print('OK')"` 輸出 OK

---

### Step 2: Provider Abstraction 骨架

**改動**：新增 `ops/scripts/crawler_providers.py`

**內容**：
- `CrawlerProvider` Protocol（4.1 節定義的介面）
- `ScrapeResult` dataclass（4.4 節定義的欄位）
- `create_provider(name: str | None = None) -> CrawlerProvider` factory function
  - 讀取環境變數 `CRAWLER_PROVIDER`（預設 `"local"`）
  - 回傳 `LocalCrawl4AIProvider()` 或 `FirecrawlProvider()`

**驗收標準**：
- [ ] `python3 -c "from crawler_providers import create_provider; p = create_provider('local'); print(type(p))"` 輸出 `<class 'LocalCrawl4AIProvider'>`
- [ ] `python3 -c "from crawler_providers import create_provider; p = create_provider('firecrawl'); print(type(p))"` 輸出 `<class 'FirecrawlProvider'>`
- [ ] unit test：`ScrapeResult` 欄位完整（success/markdown/word_count/content_hash/paywall_detected/paywall_signal/provider）

---

### Step 3: 實作 LocalCrawl4AIProvider

**改動**：`ops/scripts/crawler_providers.py` 新增 `LocalCrawl4AIProvider`

**`scrape()` 行為**：
- 使用 `crawl4ai.AsyncWebCrawler(config=BrowserConfig(headless=True))`
- `CrawlerRunConfig(markdown=True, only_main_content=True, cache_mode=CacheMode.BYPASS)`
- 呼叫 `crawler.arun(url=url, config=run_cfg)`
- 回傳 `ScrapeResult`（success/markdown/word_count/content_hash/paywall_detected/paywall_signal/provider="local"）

**`map()` 行為**：
- 使用 Crawl4AI 的 link discovery 或 `urllib` 解析 sitemap XML
- 回傳 `list[dict]`（url/title/source）

**驗收標準**：
- [ ] `python3 -c "from crawler_providers import create_provider; import asyncio; p = create_provider('local'); r = asyncio.run(p.scrape('https://www.biorxiv.org/content/10.1101/2026.01.01.123456v1')); print(r.success, r.word_count)"` 輸出 `True <positive int>`
- [ ] content_hash 非空
- [ ] paywall_detected 為 False（公開頁面）

---

### Step 4: Source-level Routing

**改動**：
- `ops/source-manifests/biotech.yaml` — 3 個 hard sources 加 `crawler_provider: firecrawl`
- `ops/scripts/run_pipeline.sh` — 讀取 source-level `crawler_provider` 並決定用哪個 provider

**路由邏輯**（`run_pipeline.sh` 內）：
```bash
# 讀取 source-level provider override（預設用全域 CRAWLER_PROVIDER）
SOURCE_PROVIDER=$(SOURCE_NAME="$SRC_NAME" python3 -c "
import yaml, os, sys
with open('ops/source-manifests/biotech.yaml') as f:
    data = yaml.safe_load(f)
for s in data['sources']:
    if s['name'].lower() == os.environ['SOURCE_NAME'].strip().lower():
        print(s.get('crawler_provider', ''))
        sys.exit(0)
print('')
" 2>/dev/null)

PROVIDER="${SOURCE_PROVIDER:-$CRAWLER_PROVIDER}"
```

**驗收標準**：
- [ ] `Endpoints News` 的 `SOURCE_PROVIDER` 輸出 `firecrawl`
- [ ] `STAT News` 的 `SOURCE_PROVIDER` 輸出空字串（用全域預設）
- [ ] 環境變數 `CRAWLER_PROVIDER=local` 時，所有非 override sources 走本地

---

### Step 5: 遷移 8 個 Easy Sources 並驗證

**來源清單**：STAT News, BioPharma Dive, Nature Biotechnology, arXiv Quantitative Biology, bioRxiv, Fierce Biotech, GEN, SynBioBeta

**驗收標準**（每個 source）：
- [ ] `scrape()` 成功（success=True）
- [ ] word_count ≥ `MIN_WORDS_FOR_LLM`（300）
- [ ] content_hash 非空且穩定（同一 URL 兩次抓取 hash 相同）
- [ ] `run_pipeline.sh` 單 source 測試通過
- [ ] 抓取成功率 ≥ 95%（跑 10 次，≤1 次失敗）

---

### Step 6: Hard Sources Fallback 驗證

**來源清單**：Endpoints News, BioCentury, Science

**驗收標準**：
- [ ] `Endpoints News`：`crawler_provider: firecrawl` 生效，走 Firecrawl `/v2/map`
- [ ] `BioCentury`：RSS 正常抓取，paywall 頁面偵測到 `paywall_detected=True`
- [ ] `Science`：RSS 正常抓取，全文 paywall 偵測正常
- [ ] `ENABLE_CLOUD_FALLBACK=false` 時，hard sources 走本地（降級，不 crash）
- [ ] `ENABLE_CLOUD_FALLBACK=true` 時，hard sources 走 Firecrawl

---

### Step 7: 清理與文件更新

**改動**：
- `ops/scripts/smoke_test.sh` — step 4 改為本地 Crawl4AI health check
- `ops/scripts/_fetch_firecrawl_credit_usage.py` — 加 `CRAWLER_PROVIDER=local` 條件
- `docs/phase1/local-crawler-stack-evaluation.md` — 加遷移完成標記
- `.env` — 加 `CRAWLER_PROVIDER=local` 預設值

**驗收標準**：
- [ ] `smoke_test.sh` 在 `CRAWLER_PROVIDER=local` 時全部 pass
- [ ] `_fetch_firecrawl_credit_usage.py` 在 local 模式不呼叫 Firecrawl API
- [ ] `.env` 有 `CRAWLER_PROVIDER=local`

---

## 7. Acceptance Criteria（DoD）

| # | 條件 | 測量方式 |
| --- | --- | --- |
| AC-1 | 8 easy sources 用本地 provider 抓取成功率 ≥ 95% | `run_pipeline.sh` 單 source 跑 10 次 |
| AC-2 | content_hash 去重率維持（不因渲染差異導致重複文章重跑 LLM） | `content_hash` 一致性測試 |
| AC-3 | LLM 分析覆蓋率 ≥ 現況（`MIN_WORDS_FOR_LLM` 通過率不降） | pipeline run log |
| AC-4 | 成本工具顯示本地 $4.32/mo | `estimate_crawler_cost.py` 輸出 |
| AC-5 | Firecrawl 路徑保留，環境變數切回 firecrawl 時原路徑正常 | `CRAWLER_PROVIDER=firecrawl` 跑 smoke_test.sh |
| AC-6 | 3 hard sources 的 `crawler_provider: firecrawl` 生效 | manifest 欄位 + pipeline log |

---

## 8. 測試計畫

### 8.1 Unit Tests

| 測試 | 內容 | 預期 |
| --- | --- | --- |
| `test_scrape_result_fields` | `ScrapeResult` 包含所有 7 個必要欄位 | pass |
| `test_content_hash_stability` | 同一 markdown 兩次 `hash_markdown()` 結果相同 | pass |
| `test_paywall_detection` | 含 `PAYWALL_MARKERS` 的 markdown 偵測為 True | pass |
| `test_provider_factory` | `create_provider("local")` 回傳 `LocalCrawl4AIProvider` | pass |

### 8.2 Integration Tests

| 測試 | 內容 | 預期 |
| --- | --- | --- |
| `test_local_scrape_biorxiv` | 本地 provider 抓 bioRxiv 公開頁 | success=True, word_count≥300 |
| `test_local_scrape_statnews` | 本地 provider 抓 STAT News | success=True, word_count≥300 |
| `test_firecrawl_provider` | Firecrawl provider 抓 STAT News | success=True（需 FIRECRAWL_KEY） |

### 8.3 回歸測試

| 測試 | 內容 | 預期 |
| --- | --- | --- |
| `smoke_test_firecrawl` | `CRAWLER_PROVIDER=firecrawl` 跑 smoke_test.sh | 全 pass |
| `smoke_test_local` | `CRAWLER_PROVIDER=local` 跑 smoke_test.sh | 全 pass |
| `pipeline_single_source` | `run_pipeline.sh` 單 source 跑完整流程 | 無 error |

---

## 9. 風險與回滾

| 風險 | 影響 | 機率 | Rollback 計畫 |
| --- | --- | --- | --- |
| 反爬封鎖（Cloudflare/PerimeterX） | 來源抓不到 | 中 | 該 source 的 `crawler_provider` 切回 `firecrawl` |
| content_hash 飄移 | 重複文章重跑 LLM | 中 | 調高 dedupe 容忍度；沿用 `hash_markdown()` normalize |
| Crawl4AI 版本升級破壞 | pipeline crash | 低 | `requirements-dev.txt` pin 版本；`pip install crawl4ai==0.9.3` |
| Ollama 不可用 | LLM 分析失敗 | 低 | 沿用現有 fallback（跳過 LLM，只存 markdown） |
| Playwright chromium crash | 單頁抓取失敗 | 低 | retry 邏輯（沿用 `MAX_ATTEMPTS` pattern）；必要時切 Firecrawl |

**通用 rollback**：所有變更透過環境變數控制。出問題時設定 `CRAWLER_PROVIDER=firecrawl` + 移除 manifest 中的 `crawler_provider` override 即可回到原狀。

---

## 10. 參考資料

| 資料 | 路徑 / URL |
| --- | --- |
| 本地 Crawler Stack 評估 memo | `docs/phase1/local-crawler-stack-evaluation.md` |
| Crawl4AI PoC 腳本 | `ops/poc/crawl4ai_poc.py` |
| 成本估算工具 | `ops/scripts/estimate_crawler_cost.py` |
| Source manifest | `ops/source-manifests/biotech.yaml` |
| Crawl4AI 官方文件 | https://docs.crawl4ai.com/ |
| Playwright Python 文件 | https://playwright.dev/python/ |
| Trafilatura 文件 | https://trafilatura.readthedocs.io/ |
| Phase 1 Engineering Spec（格式參考） | `docs/koji/02-engineering-spec-phase1.md` |
| Firecrawl API 文件 | https://docs.firecrawl.dev/ |
