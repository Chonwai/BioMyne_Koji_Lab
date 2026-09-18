# Crawl4AI P2 — 反爬實測快照（8 Easy Sources × Local Provider）

## Document Status

| Field | Value |
| --- | --- |
| Status | 實測快照（P2 Step 2 anti-bot 實測） |
| Date | 2026-09-19 |
| Type | 實測紀錄（Evidence / Snapshot，非權威文檔） |
| 上層文檔 | `crawl4ai-migration-overview.md`、`crawl4ai-migration-engineering-spec.md`、`crawl4ai-migration-feasibility-review.md` |
| 環境 | `.venv` Python 3.12.9、crawl4ai==0.9.3、playwright 1.63.0 |

## Executive Summary

針對 8 個 easy sources 每個取 1 篇**實際文章 URL**，以 **LocalCrawl4AIProvider**（`_scrape_via_provider.py <url> local`）實測全文抓取，**8/8 全部 success=True**，word_count 全部 > 100（範圍 848–2690，MIN_WORDS_FOR_LLM=100）。STAT News 與 Fierce Biotech（feasibility review 標記為 Cloudflare 風險）額外各測 3 篇（共 4 篇/來源），**8/8 也全部成功**，無 403、無 timeout、無 paywall marker。**結論：8 個 easy sources 全數 ✅ 可直接遷移 local provider，無需 per-domain 調校即可通過 P2 Step 2 閘門。**

## 1. 實測矩陣（8 Sources × 1 篇 / Source）

| Source | 文章 URL | success | word_count | 花費 | 判定 |
|---|---|---|---|---|---|
| STAT News | `https://www.statnews.com/2026/09/18/hca-hospitals-sue-independence-blue-cross-prior-authorization/` | ✅ true | 1484 | 10.6s | ✅ |
| BioPharma Dive | `https://www.biopharmadive.com/news/xenon-azetukalner-depression-trial-halt-adverse-events/830756/` | ✅ true | 2140 | 11.4s | ✅ |
| Nature Biotechnology | `https://www.nature.com/articles/s41587-026-03333-8` | ✅ true | 2690 | 11.5s | ✅ |
| arXiv q-bio | `https://arxiv.org/abs/2609.19190` | ✅ true | 848 | 13.9s | ✅ |
| bioRxiv | `https://www.biorxiv.org/content/10.64898/2026.01.12.699030` | ✅ true | 1817 | 15.6s | ✅ |
| Fierce Biotech | `https://www.fiercebiotech.com/biotech/refreshed-novo-corrals-three-new-early-stage-obesity-drugs-kallyope` | ✅ true | 933 | 19.8s | ✅ |
| GEN | `https://www.genengnews.com/topics/translational-medicine/time-restricted-eating-linked-to-improved-huntingtons-disease-markers/` | ✅ true | 1626 | 11.2s | ✅ |
| SynBioBeta | `https://www.synbiobeta.com/read/one-model-every-microbiome` | ✅ true | 2629 | 11.6s | ✅ |

- 判定基準：word_count ≥ 100（`MIN_WORDS_FOR_LLM` repo 預設）→ ✅ 可抓取；< 100 或 success=False → ⚠️/❌
- provider 全數 `local`；paywall_detected 全數 False
- 花費統計：avg ≈ 13.2s，最慢 Fierce 19.8s、arXiv 13.9s（多一次 redirect），最快 STAT 10.6s

## 2. 額外實測：STAT News × 4、Fierce Biotech × 4（Cloudflare 風險來源）

feasibility review（NB-4）標記 STAT（Cloudflare + Boston Globe Media 封鎖 bots + tinypass paywall）與 Fierce（Cloudflare）為最高風險。以下為 RSS 直達 + 全文抓取的額外驗證。

| Source | 文章 URL | success | word_count | 花費 | 判定 |
|---|---|---|---|---|---|
| STAT-1 | `.../2026/09/18/hca-hospitals-sue-independence-blue-cross-prior-authorization/` | ✅ | 1484 | 10.6s | ✅ |
| STAT-2 | `https://www.statnews.com/2026/09/18/biotech-news-roche-expands-it-boston-footprint-with-research-center/` | ✅ | 2002 | 9.9s | ✅ |
| STAT-3 | `https://www.statnews.com/pharmalot/2026/09/18/up-down-ladder-latest-comings-goings-job-changes/` | ✅ | 1821 | 7.8s | ✅ |
| STAT-4 | `https://www.statnews.com/2026/09/18/health-news-who-supports-health-equity-policy-in-america/` | ✅ | 2177 | 10.2s | ✅ |
| Fierce-1 | `https://www.fiercebiotech.com/biotech/refreshed-novo-corrals-three-new-early-stage-obesity-drugs-kallyope` | ✅ | 933 | 19.8s | ✅ |
| Fierce-2 | `https://www.fiercebiotech.com/biotech/inside-growing-world-biopharma-prediction-markets` | ✅ | 576 | 11.8s | ✅ |
| Fierce-3 | `https://www.fiercebiotech.com/medtech/medtronic-earns-fda-clearance-liagsure-use-its-hugo-robotic-system` | ✅ | 694 | 11.7s | ✅ |
| Fierce-4 | `https://www.fiercebiotech.com/biotech/chutes-ladders-legend-poaches-novartis-vet-boost-commercial-potential` | ✅ | 1522 | 21.7s | ✅ |

- **STAT News 4/4 全通**，word_count 1484–2177，無 paywall marker、無 403
- **Fierce Biotech 4/4 全通**，word_count 576–1522（最低 576 仍遠超 100），無 403、無 timeout
- 失敗原因記錄：**無失敗**（無 403 / timeout / paywall marker）

## 3. 判定摘要

| 結論 | Sources | 依據 |
|---|---|---|
| ✅ 可直接遷移 | 8/8（STAT/BioPharma Dive/Nature/arXiv/bioRxiv/Fierce/GEN/SynBioBeta） | 8/8 success=true、word_count 全 >100、無 paywall |
| ⚠️ 需調校 | 無 | — |
| ❌ 需回滾 Cloud | 無 | — |

- 額外樣本（STAT/Fierce 各 4 篇）也全數過關 → Cloudflare 風險來源在 RSS 直達 + Crawl4AI 本地渲染路徑下未觸發任何阻擋
- **注意**：本實測為「RSS/sitemap/category 找到的文章 URL」→ 全文抓取；feasibility review 的 Cloudflare 風險主要針對「非 RSS 路徑（如直接打 homepage / 泛用 map）」與「連發頻率」，本輪未覆蓋。P2 實際運轉時若某 source 出現 403/timeout/paywall 任一訊號，依 spec rollback gate 切回 `firecrawl_cloud`。

## 4. 觀察與 finding（供後續 loop）

| # | 類型 | 發現 | 建議 |
|---|---|---|---|
| F-a | ⚠️ 低 | bioRxiv `connect.biorxiv.org/relate/feed/biorxiv.xml` 實測**空回應**（非 XML），連三次不同日期 API 查詢有 1 次空、1 次需完整 browser-UA 才回 JSON | category_page/API discovery 路徑需在 P2 運轉前再驗證；本次是經 biorxiv.org API 找到 DOI |
| F-b | ⚠️ 低 | SynBioBeta 首頁第一個 article-like link 被外連 promo 佔據；文章實際在 `/read/<slug>` 路徑 | category_page parser 需注意非 article link（promo/events/jobs）過濾 |
| F-c | ℹ️ 觀察 | arXiv `abs/` 頁 word_count 848 為 14 篇中最低；若後續 content_hash 測試需要低變異來源，arXiv 是候選 | — |
| F-d | ℹ️ 觀察 | 單篇本地抓取耗時 7.8–21.7s（avg ~13s），無 LLM 參與（markdown-only）。若 P1 含 LLM extraction（~5–9 min/篇）需延遲預算出線 | 與 POC 紀錄一致 |

## 5. 重跑方法

```bash
cd /Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji
.venv/bin/python3 ops/scripts/_scrape_via_provider.py "<ARTICLE_URL>" "local" 2>/dev/null \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps({"success": d.get("success"), "word_count": d.get("word_count"), "provider": d.get("provider"), "error": d.get("error","")[:100]}, ensure_ascii=False))'
```