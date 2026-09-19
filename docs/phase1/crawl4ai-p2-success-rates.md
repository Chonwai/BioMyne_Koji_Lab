# Crawl4AI P2 — 20 Runs 成功率統計報告

## Document Status

| Field | Value |
| --- | --- |
| Status | 實測報告（P2 Step 4 AC-1 驗證） |
| Date | 2026-09-20 |
| Type | 實測紀錄（Evidence / Report） |
| 環境 | .venv Python 3.12.9、crawl4ai==0.9.3、Mac Studio M5 Ultra 96GB |
| 方法 | 8 sources 並行 × 20 runs = 160 次本地 provider scrape（Bash 3.2 compatible） |

## Executive Summary

**AC-1 全線通過**：8 個 easy sources 以本地 `LocalCrawl4AIProvider` 抓取，**160/160 runs（100%）全部成功**。平均成功率 100%（spec 標準 ≥95%），最低單一 source 也是 100%（spec 標準 ≥80%）。無 403、無 timeout、無 paywall marker。反爬風險全面低於預期。

## 實測結果

| Source | success | fail | rate | avg_word_count | 判定 |
| --- | --- | --- | --- | --- | --- |
| arXiv Quantitative Biology | 20 | 0 | **100.0%** | 723 | ✅ AC-1 PASS |
| STAT News | 20 | 0 | **100.0%** | 930 | ✅ AC-1 PASS |
| BioPharma Dive | 20 | 0 | **100.0%** | 1147 | ✅ AC-1 PASS |
| Nature Biotechnology | 20 | 0 | **100.0%** | 2217 | ✅ AC-1 PASS |
| bioRxiv | 20 | 0 | **100.0%** | 763 | ✅ AC-1 PASS |
| Fierce Biotech | 20 | 0 | **100.0%** | 525 | ✅ AC-1 PASS |
| GEN | 20 | 0 | **100.0%** | 1199 | ✅ AC-1 PASS |
| SynBioBeta | 20 | 0 | **100.0%** | 2482 | ✅ AC-1 PASS |
| **平均 / 合計** | **160** | **0** | **100.0%** | **1136** | **✅ PASS** |

## AC-1 驗收對照

| AC-1 條件 | 標準 | 實測結果 | 判定 |
| --- | --- | --- | --- |
| 8 sources 平均抓取成功率 | ≥ 95% | **100.0%** | ✅ PASS（+5.0%） |
| 單一 source 最低成功率 | ≥ 80% | **100.0%**（最低 = Fierce Biotech） | ✅ PASS（+20%） |
| 樣本量 | 每 source 20 runs | 160 runs（8×20） | ✅ |

## 關鍵觀察

1. **反爬風險全面低於預期**：feasibility review 預測 STAT/Fierce 在 Cloudflare 後（NB-4），**實測 40/40 runs 全通**（各 20 runs）— RSS 直達 + 全文抓取均無障礙
2. **word_count 變異**：Fierce 最低（525 avg）但仍遠超 `MIN_WORDS_FOR_LLM`（100）；SynBioBeta 最高（2482）；**fit_markdown + boilerplate exclusion** 正常運作（STAT 760 = 純正文）
3. **平均抓取時間**：依 Step 2 實測約 13.2s/run（160 runs ≈ 35 分鐘並行完成）
4. **hash 穩定性已驗證**（Step 3）：fit_markdown + boilerplate exclusion 後 5/5 = 100%（之前 40% 未修復時）

## 殘留項目

- ⚠️ sql/006 尚未 apply 到 live Supabase（現由 migration 工具問題處理中 — 見 DB migration 方案討論）
- ⚠️ LLM extraction 延遲（~5.4 min/warm）— Mac Studio M5 Ultra 上待驗證（用戶報告快很多倍）
