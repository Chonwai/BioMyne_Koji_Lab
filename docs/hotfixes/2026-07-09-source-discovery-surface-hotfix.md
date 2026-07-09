# Hotfix Post-Mortem: Source discovery surface drift and fallback suppression

**Date:** 2026-07-09
**Severity:** P2 (High)
**Reported by:** 手動管線觸發 (`run_pipeline.sh`)
**Time to Resolution:** ~2 hours
**Fix Author:** agent (GitHub Copilot)

## Timeline

- `00:11` 手動管線觸發，7 個來源出現 `0 candidate articles` 或 `404 category target`
- `00:20` 重現確認：直接跑 `_discover_article_urls.py` 後，發現部分來源單獨可出候選、但帶 live state 時會被錯誤 surface 短路
- `00:40` 根因分流完成：parser bug、source-rule drift、category-page control-flow bug、以及少數正常的 no-new 情境被混在一起
- `01:30` hotfix 完成並做多輪 helper 驗證

## Bug Summary

`2026-07-09` 的 manual pipeline run 中，`arXiv`、`bioRxiv`、`Science`、`GEN`、`Endpoints News`、`SynBioBeta`、`BioCentury` 被一起視為「失效來源」，但實際上混合了四種不同情況：

1. **真實 runtime 缺陷**
   - `Science` 的 RSS 是 RSS 1.0 / RDF，現有 parser 只處理 RSS 2.0 / Atom
   - `GEN` 的文章 URL 走 `/topics/{vertical}/{slug}`，卻被全域 taxonomy filter 誤殺
   - `Endpoints` 文章 URL 多數是 root slug，原本 scoring 規則分數不夠進不了候選
   - `category_page` surface 在「target 不到期」或「全部 target 失敗」時會回空陣列，但上層把它當作成功，導致不會 fallback

2. **來源結構漂移 / 舊假設失效**
   - `bioRxiv` 當前 recent article URL 不再只用 `10.1101`，也出現 `10.64898`
   - `BioCentury` 其實存在可用 feed：`https://www.biocentury.com/rss/BioCentury.xml`
   - `SynBioBeta` 沒有穩定 RSS，但有更乾淨的 listing：`/synthetic-bio-news`
  - `bioRxiv` recent page 的 anchor 排序不保證嚴格 newest-first，不能安全依賴 `last_seen_url` 早停

3. **正常 no-new，不是故障**
   - `arXiv` 在帶 live cursor 時返回 `0`，是因為 feed cursor 已經在最新時間點
   - 修復後再跑 `Science` / `GEN` 返回 `0`，是因為第一次 hotfix 驗證已推進 cursor

## Root Cause

**表象：** 多個來源同時 `0 candidate`，看起來像整體 crawling strategy 失效。

**根因：** 實際上是「多個局部缺陷 + 舊 surface 假設 + 正常 cursor 行為」疊加：

- parser 層：`fetch_feed_entries()` 沒處理 RDF root
- scoring 層：source-specific include / exclude 規則沒有跟上網站 URL 結構
- control-flow 層：`category_page_candidates()` 的 `None / error / empty-success` 沒有被上層區分
- cursor 層：`bioRxiv` category page 若使用 `last_seen_url` 早停，會因頁面排序不穩而提前截斷新文章
- config 層：manifest 還把 `bioRxiv` / `BioCentury` / `SynBioBeta` 指向舊的 primary surface 假設

## Fix Applied

### Runtime logic

- `ops/scripts/_discover_article_urls.py`
  - 新增 RSS 1.0 / RDF feed parsing
  - 讓 `category_page` primary surface 可以每個 tick 都執行，不再被 `check_frequency` 短路
  - `category_page` 若 target 全失敗，改為顯式 fallback，而不是靜默成功
  - 擴大 `bioRxiv` DOI matching 規則（不再只認 `10.1101`）
  - 對 `bioRxiv` 關閉脆弱的 `last_seen_url` 早停捷徑，改靠全域 dedupe / refresh 控制重複
  - 修正 `GEN` `/topics/...` article path 與 `Endpoints` root-slug article path 的 scoring
  - 排除 `SynBioBeta` 首頁 root link 被誤當文章

### Repo config / future seed

- `ops/source-manifests/biotech.yaml`
  - `bioRxiv` 改為 `category_page` primary
  - `SynBioBeta` 改為 `category_page` primary
  - `BioCentury` 改為 `rss` primary，feed URL 指向 `rss/BioCentury.xml`

- `sql/005_p2b_refresh_and_category_targets.sql`
  - `BioCentury` category target 由失效的 `/biopharma` 改成 `/analysis/articles`
  - `SynBioBeta` category target 改成 `/synthetic-bio-news`
  - `bioRxiv` / `SynBioBeta` target cadence 調整為更適合 listing-first 的設定

## Validation

### First-pass live helper validation

- `Science`：`rss -> 20 candidates`
- `GEN`：`rss -> 10 candidates`
- `Endpoints News`：`map -> 20 candidates`
- `BioCentury`：`map -> 20 candidates`
- `bioRxiv`：仍失敗，暴露 `category_page` primary 受 `check_frequency` 短路的第二個局部 defect

### Second-pass validation after follow-up repair

- `bioRxiv`：`category_page -> 14 candidates`
- `BioCentury`：`rss -> 20 candidates`
- `Endpoints News`：`map -> 20 candidates`
- `SynBioBeta`：category-page dry-run 僅剩 `/read/` article links，不再混入首頁 root link

### Expected non-error cases confirmed

- `arXiv`：帶 state 時 `0 candidates` 是 cursor 已在最新 feed bucket，不是 parser/URL 錯誤
- `Science` / `GEN` 二次驗證歸零，是第一次 hotfix 驗證已推進 cursor

## Follow-up Hardening (Strict 100-point pass)

在第一次 hotfix 後，新的 manual run 又暴露了三個更細的品質問題：

1. `bioRxiv` article scrape 會間歇性命中 Firecrawl `SCRAPE_TIMEOUT`
2. `Endpoints` / `Fierce` discovery 偶發 `TLS/SSL EOF`，顯示 feed/html/map transport 還不夠韌性
3. `Endpoints` / `BioCentury` 的 paywalled teaser 雖然不再報錯，但若直接進 LLM 會污染 digest 品質；另外 `Endpoints` 還混入一筆 `topic-hub/.../page/N` 聚合頁

### Additional fixes applied

- `ops/scripts/_scrape_markdown.py`
  - Firecrawl scrape timeout 改成可配置、逐次遞增，並對 `bioRxiv` / `arXiv` / scholarly hosts 增加額外 headroom
  - 輸出 `paywall_detected` 與 `paywall_signal`

- `ops/scripts/run_pipeline.sh`
  - 若 scrape 結果命中 paywall/subscriber gate，直接保留 teaser/raw markdown 並跳過 LLM
  - teaser summary 明確標成 limited-access intelligence，而不是假裝完整摘要

- `ops/scripts/_discover_article_urls.py`
  - feed / sitemap / HTML fetch 改為有 retry 的 shared HTTP path
  - Firecrawl map timeout / retry 也提升
  - `Endpoints` 排除 `topic-hub/` 與 `.../page/N` 聚合頁
  - `arXiv` 啟用 coarse timestamp cursor 模式，使用 `last_cursor_url` 避免同一時間桶漏稿

### Final validation

- sample scrape 驗證：
  - `bioRxiv` full article scrape 成功，`word_count=1348`
  - `Endpoints` sample 正確標記 `signup_gate`
  - `BioCentury` sample 正確標記 `purchase_gate`
- arXiv regression：在 `last_cursor_published_at == first entry timestamp` 的情況下，仍可保留同一時間桶的其餘 candidates（`candidate_count=20`）
- full pipeline run `c705d260-0616-4289-8169-65dafd557127`：`Articles=51`, `Errors=0`
- final confirmatory run `63d3e588-6745-4e5a-8763-5554486927ce`：`Articles=7`, `Errors=0`，且 `Endpoints` 只剩真實 article teaser，不再混入 topic-hub 聚合頁

## Residual Risks

- `Endpoints News` 與 `BioCentury` 仍受 publisher access policy 限制，所以目前最佳策略是明確標記 teaser / limited-access content，而不是偽裝成完整文章
- `source_category_targets` 的 repo seed 與 live rows 已對齊本次 hotfix 路線，但若未來 publisher 再改版，仍需重新做 surface audit

## Prevention Actions

- [ ] 為 feed parser 補一個 regression fixture：覆蓋 RSS 2.0、Atom、RSS 1.0 / RDF 三種 root
- [ ] 為 source rules 增加 per-source URL contract regression checks（至少覆蓋 `GEN`、`Endpoints`、`bioRxiv`）
- [ ] 將 live `source_category_targets` 與 repo seed 對齊，避免 repo 修好了但 DB 仍保留舊 target URL
- [ ] 若後續觀察到 `arXiv` 同日漏稿，補 `last_cursor_url` 或 entry id cursor refinement