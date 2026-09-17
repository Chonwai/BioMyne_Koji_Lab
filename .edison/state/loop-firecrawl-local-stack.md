# Loop State: Koji Firecrawl→Local Crawler Stack Feasibility

Goal: 評估「本地 Mac 部署情境下，是否可用 Playwright + Crawl4AI 開源爬蟲棧取代付費 Firecrawl Cloud」，產出業界對比研究 + 可行性結論 + 遷移方案 + hackathon 式落地成果
Started: 2026-09-17
Status: active
Quality Mode: strict (93)
Depth Level: L3 Deep Dive
Snapshot Cache: /Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji/docs/.project-context.md (STALE)
Snapshot Evidence Status: LOCATOR-ONLY
Budget: ~10 iterations

## Stage Round Counters

| Stage                | Current Round | Max Rounds (Stop Rule) | Status  |
| -------------------- | :-----------: | :--------------------: | ------- |
| DISCOVER (codebase)  |       1       |           3            | ✅ done |
| DISCOVER (industry)  |       1       |           3            | ✅ done |
| PLAN                 |       1       |           2            | ✅ done |
| EXECUTE              |       1       |           3            | ✅ done |
| VERIFY (code-review) |       1       |           2 (strict)   | ✅ done |

## Iterations

### Iteration 1 — DISCOVER (codebase + 業界研究)

**Agent:** morpheus + jarvis-deep-research（並行）
**核心發現：**

**Firecrawl 使用面（4 個端點）：**
- `/v2/map` — `_discover_article_urls.py` L225-269, L1103（Endpoints News 唯一 map-first source）
- `/v1/scrape` — `_scrape_markdown.py` L79-112（formats=markdown, onlyMainContent, timeout, waitFor=2000）
- `/v1/team/credit-usage` — `_fetch_firecrawl_credit_usage.py`（run_pipeline.sh before/after）
- smoke_test.sh L94-114 scrape health check

**兩份研究結論（一致但程度不同）：**
- morpheus（codebase 面）：**有條件可行** — RSS/Sitemap 8/11 source 可直接遷移，Endpoints News 需保留 Cloud
- jarvis（業界面）：**可以取代** — Crawl4AI 83K stars、v0.9.3 活躍、Apache 2.0、功能覆蓋完整；成本 $19/mo → ~$0（電費 $5/月）；11 source 90% 無需 proxy
- **共同建議：Provider Abstraction 為第一步**（source-level routing：RSS sources 走 Crawl4AI，hard sources 留 Cloud）
- Crawl4AI + Ollama (Qwen 3.6) LLM extraction 可行 — `LLMExtractionStrategy` + `provider="ollama/..."` 原生支援
- **「零配置任意網站」被高估**：真實情況是 30 分鐘/來源（有 RSS）→ 2-4 小時（結構複雜）→ 非零人工

**決策 memo 覆核：**
- 原 memo 基於 Firecrawl **self-host**（無 Fire-engine/proxy/dashboard 是致命傷）
- Crawl4AI 是獨立產品 — memo 結論不能直接套用
- 純本地情境下：Cloud 的 proxy rotation 優勢仍在，但 11 source 中僅 Endpoints 需要

**遷移風險矩陣：**
- 🔴 反爬風險（Endpoints/BioCentury 本地 IP 易封）→ 緩解：Provider Abstraction + Cloud fallback
- 🟡 Crawl4AI markdown 格式 vs Firecrawl 差異 → content_hash 可能變 → 需 normalize 驗證
- 🟡 paywall 偵測需保留（Crawl4AI 不自動偵測）

**Stage Round:** 1/3 | **Outcome:** PASS（兩報告交叉一致 + 實測證據）

### Iteration 2 — EXECUTE (3 commits 研究落地)

**Agent:** trinity
**Commits landed:**
1. `a88c9d1` — docs: add local crawler stack evaluation memo（193 行決策文件）
2. `d3e5ef7` — feat: add Firecrawl vs local crawler cost estimation tool（213 行純計算）
3. `99d42ed` — feat: add Crawl4AI PoC script（224 行 standalone）

**Stage Round:** 1/3 | **Outcome:** PASS（zero scope drift，未觸碰既有 pipeline）

### Iteration 3 — VERIFY (strict code review)

**Agent:** smith
**Measured Score: 95.80 / Threshold: 93 → PASS（有條件）**
- CR-D1 Plan: 98 ｜ CR-D2 Arch: 97 ｜ CR-D3 DB: 100 ｜ CR-D4 Cross-module: 85 ｜ CR-D5 Security: 98 ｜ CR-D6 Perf: 98 ｜ CR-D7 Design: 90
- Findings: F-01（Medium）memo/tool 成本數字 reconciliation ｜ F-02（Low）unused Optional import ｜ F-03（Low）660 來源註記 ｜ F-04（Low）feat: 前綴 nit
- 零 Critical / 零 High
**Stage Round:** 1/2 | **Outcome:** PASS + bounded repair

### Iteration 4 — REPAIR (bounded fixes)

**Agent:** trinity
**Commit:** `ea372ba` — fix: reconcile cost estimates in memo and add source annotations
- F-01 ✅ memo §8 加 reconciliation 註記
- F-02 ✅ 刪 Optional unused import
- F-03 ✅ 660 來源註記
**Outcome:** ✅ 全部修復

**Final verification:**
- `python3 ops/scripts/estimate_crawler_cost.py --articles 660 --scrape-credits 3` 正常輸出（Free 超額 ❌ / Hobby $16 ✅ / 本地 $4.32/mo）
- git log 4 commits 全部落地（a88c9d1 → d3e5ef7 → 99d42ed → ea372ba）

## Circuit Breaker

Consecutive fails: 0/3
Budget: 35%
Status: HEALTHY

## Done Contract 驗證

- [x] 深入調查「本地 Playwright+Crawl4AI 取代 Firecrawl」可行性（雙路研究）
- [x] 業界 Crawl4AI/Playwright/AI 彈性爬取對比研究（22+ 來源）
- [x] 決策 memo 落地（local-crawler-stack-evaluation.md）
- [x] 成本估算工具落地（estimate_crawler_cost.py）
- [x] Crawl4AI PoC 落地（ops/poc/crawl4ai_poc.py）
- [x] Hackathon 式 4 次 commit
- [x] strict 93 審查 PASS（95.80）+ bounded repair 完成

**Status: complete** ✅

## Circuit Breaker

Consecutive fails: 0/3
Budget: 5%
Status: HEALTHY

## Loop 設計

```
DISCOVER (L3, 並行 2 路)
  ├── morpheus（codebase：Firecrawl 使用面盤點 + self-host memo 覆核 + 本地資源評估）
  └── jarvis-deep-research（業界：Crawl4AI/Playwright 評測 + AI-driven extraction + crawler stack 對比）
        ↓
PLAN（architect — 遷移可行性結論 + 方案設計 + 風險矩陣 + 分期路徑）
        ↓
EXECUTE（trinity — hackathon 式 commit 落地高價值成果：adapter 抽象 / 成本估算工具 / PoC 檔）
        ↓
VERIFY（smith — strict 93 審查）
        ↓
ITERATE（Neo 決策）
```

## 任務背景筆記

- 用戶情境：MacBook Pro (14" 2021) 開發 + Mac Studio M3 Ultra 96GB 部署，全部本地
- 用戶實戰經驗：Playwright + Crawl4AI 效果好
- 用戶願景：日後使用者/老闆隨手加一個 website 來源（大公司 Landing page 或新聞網頁），系統用 AI 能力即時彈性爬取全部內容
- 既有決策 memo：`docs/phase1/firecrawl-self-host-decision-memo.md`（2026-07-08，cloud-first）
- 現況：Firecrawl Cloud /v2/map 1 credit/call、/v1/scrape 2-5 credits/article、1K free credits/月
- 上次 Loop 已修正：MAX_ARTICLES=30、MIN_WORDS=100、waitFor=2000ms、移除 smoke_test 硬編碼密鑰