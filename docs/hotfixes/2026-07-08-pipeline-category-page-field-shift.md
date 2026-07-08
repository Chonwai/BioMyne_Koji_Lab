# Hotfix Post-Mortem: Pipeline category-page candidate 欄位錯位

**Date:** 2026-07-08
**Severity:** P2 (High)
**Reported by:** 手動管線觸發 (`run_pipeline.sh`)
**Time to Resolution:** ~35 minutes
**Fix Author:** agent (GitHub Copilot)

## Timeline

- `20:30` 手動管線觸發，run `a00ee282-c880-40bf-bad2-f276396942a3` 開始
- `20:31` 發現多個 source 寫入失敗，錯誤為 `invalid input syntax for type timestamp with time zone`
- `20:40` 重現確認：失敗 payload 的 `published_at` 被寫成 `category_page` / `new`
- `20:47` 根因確認：`run_pipeline.sh` 以 tab 分隔 candidate 欄位，空的 `published_at` 造成 shell `read` 欄位左移
- `20:55` hotfix 完成，空欄位解析驗證通過

## Bug Summary

Pipeline 在處理 `category_page` 發現來源時，凡是無法推導 `published_at` 的文章，後續寫入 payload 會把 `discovery_method` 或 `processing_lane` 錯塞到 `published_at`。Supabase 因 `articles.published_at` 是 `timestamptz`，最終返回 `22007 invalid input syntax for type timestamp with time zone`。

受影響來源包含：`Fierce Biotech`、`SynBioBeta`，以及 `STAT News` 中無法推導日期的部份 candidate。

## Root Cause

`ops/scripts/run_pipeline.sh` 將 discovery candidate 轉成 tab-separated 欄位，再用：

```bash
while IFS=$'\t' read -r ARTICLE_URL TITLE_HINT SCORE_HINT PUBLISHED_AT_HINT DISCOVERY_METHOD_HINT PROCESSING_LANE EXISTING_ARTICLE_ID EXISTING_CONTENT_HASH
```

讀回 shell 變數。當 `published_at` 是空字串時，連續 tab 會被 shell 視為同一段 IFS whitespace，導致空欄位被吞掉，後方欄位整體左移：

- `published_at=""` 變成 `published_at="category_page"`
- `discovery_method="category_page"` 變成 `discovery_method="new"`

這不是 Supabase schema 問題，也不是 discovery helper 產出的 candidate dict 錯誤，而是 **shell 欄位傳遞層** 在遇到空中間欄位時發生錯位。

## Fix Applied

將 `run_pipeline.sh` 內 candidate 傳遞格式從 tab-separated 改為非空白分隔符 `\x1f`（unit separator），避免 shell `read` 把空中間欄位折疊。

Files modified:

- `ops/scripts/run_pipeline.sh` — candidate 跨程序分隔符改為 `\x1f`，並在 Python 輸出端統一清理控制字元

## Why It Wasn't Caught Earlier

- 先前驗證多集中在 RSS / sitemap 路徑，`published_at` 通常存在
- 問題只會在 `category_page` 路徑且 `published_at` 無法由 URL 推導時出現
- shell 的 IFS whitespace 行為不直觀，空欄位在 tab 分隔下會被吞掉

## Prevention Actions

- [ ] 為 candidate transport 加一個 regression check：覆蓋 `published_at=""` 的中間空欄位案例 — assigned to: team
- [ ] 評估把 shell 分隔欄位改成 JSON-lines / structured transport，降低欄位錯位風險 — tracked in: next sprint
- [ ] 針對 `STAT News` / `SynBioBeta` category-page discovery 補過濾規則，排除首頁、登入頁、帳號頁等非文章 URL — tracked in: next sprint
- [ ] 針對 `Nature Biotechnology` TLS EOF、`Endpoints News` 403、`BioCentury` 404 分開建 issue，不與本 hotfix 混修 — assigned to: team