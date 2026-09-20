# Crawl4AI P3+P4 驗證報告

## Document Status
| Field | Value |
| --- | --- |
| Status | 驗證報告（P3 Hard sources + P4 Free fallback） |
| Date | 2026-09-20 |
| Type | 實測紀錄 |

## P3 — Hard Sources Cloud Fallback 驗證（spec Step 6）

### 情境 A — 穩態（CRAWLER_ALLOW_CLOUD=true）

| Source | 測試 | 結果 | 判定 |
|---|---|---|---|
| Endpoints News | FirecrawlProvider.map('/') | 3 links 回傳（moonwalk-raises-70M 等） | ✅ |
| Endpoints News | FirecrawlProvider.scrape(首頁) | success=True, 2683 words | ✅ |
| BioCentury | FirecrawlProvider.scrape(RSS xml) | success=True, 1964 words | ✅ |
| Science | FirecrawlProvider.scrape(新聞頁) | success=True, 102 words | ✅ |

**結論**：3 個 hard sources 走 Firecrawl Cloud 全部成功（spec §4.3 第 2 層 `crawler_provider='firecrawl_cloud'` 生效）

### 情境 B — kill-switch（CRAWLER_ALLOW_CLOUD=false）

| 測試 | 結果 | 判定 |
|---|---|---|
| run_pipeline 決策（DB=firecrawl_cloud + ALLOW_CLOUD=false） | PROVIDER=local（kill-switch 壓過 DB） | ✅ |
| Endpoints 文章走 local provider | success=True, 264 words, provider=local | ✅ |

**結論**：kill-switch 生效，hard sources 走本地、不 crash（degraded 模式）

## P4 — Firecrawl Free tier 最後防線

| 驗證 | 結果 | 判定 |
|---|---|---|
| credit-usage API | remaining_credits=1021（Free tier 1000 + bonus） | ✅ |
| `_fetch_firecrawl_credit_usage.py` 條件化（ALLOW_CLOUD=false） | 回 `{skipped: local-only mode}`，不呼叫 API | ✅ |
| `_fetch_firecrawl_credit_usage.py` 條件化（ALLOW_CLOUD=true） | remaining_credits=1017（正常呼叫） | ✅ |

**結論**：Free tier 1,000 credits/mo 已在用；local-only 模式自動跳過 credit 觀測（成本封頂）

## E2E 端到端（arXiv 樣本文章）

| 步驟 | 結果 | 判定 |
|---|---|---|
| Local provider scrape | success=True, 723 words, hash=7395f24f989c | ✅ |
| Hash 穩定（重抓） | 相同（7395f24f989c... == 7395f24f989c...） | ✅ |
| LLM extraction（Ollama） | 背景執行中（P0 已驗證可行） | ⏳ |

## 結論

**P3 + P4 全部通過**：hard sources 走 Cloud fallback 正常、kill-switch 安全、Free tier 成本封頂。
