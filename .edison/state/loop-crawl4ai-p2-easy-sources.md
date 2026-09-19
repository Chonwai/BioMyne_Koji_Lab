# Loop State: Crawl4AI 遷移 P2 — Easy Sources 遷移

Goal: 正式啟動 P2（spec Step 5）：8 個 easy sources 遷移至本地 provider + 反爬實測（未知數 2）+ content_hash 穩定率驗證（≥80%）+ 20 runs 成功率統計（平均≥95%/單一≥80%）+ SUPABASE apply sql/006 + sources 表 crawler_provider 更新。達 strict 93 閘門。hackathon 式多 commit。
Started: 2026-09-19
Status: active
Quality Mode: strict (93)
Depth Level: L3 Deep Dive
Snapshot Cache: /Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji/docs/.project-context.md (STALE)
Snapshot Evidence Status: LOCATOR-ONLY — 快取僅供定位，Critical findings 必須實時 scan 驗證
Budget: ~16 iterations

## 前置狀態（P0/P1 已通過）

- P0 PoC：✅ Crawl4AI 0.9.3 + Ollama qwen3.6:35b-mlx 端到端跑通（PASS）
- P1 Provider Abstraction：✅ PASS 95.25/93（crawler_providers.py + 接線 + 26 tests）
- P2 前置 Review：✅ PASS 94.10/93（F-6/F-8 修復、22 commits 已推送）
- 環境：.venv（Python 3.12.9）+ crawl4ai==0.9.3 + playwright + trafilatura

## 8 個 Easy Sources（spec §2.2 / Step 5）

| # | Source | primary | fallback |
| --- | --- | --- | --- |
| 1 | STAT News | rss | map |
| 2 | BioPharma Dive | rss | map |
| 3 | Nature Biotechnology | sitemap | map |
| 4 | arXiv Quantitative Biology | rss | map |
| 5 | bioRxiv | category_page | map |
| 6 | Fierce Biotech | rss | map |
| 7 | GEN | rss | map |
| 8 | SynBioBeta | category_page | map |

## Stage Round Counters（v4.3）

| Stage | Current Round | Max Rounds | Status |
| --- | :---: | :---: | --- |
| DISCOVER（反爬現況 + Supabase） | 1 | 2 | ✅ done（Iteration 1） |
| EXECUTE-Step1（sql/006 apply + DB 更新） | 0 | 2 | 🔴 **BLOCKED**（Supabase NXDOMAIN） |
| EXECUTE-Step2（反爬實測） | 1 | 2 | ✅ done（Iteration 2 — 8/8 ✅） |
| EXECUTE-Step3（content_hash 穩定率） | 0 | 2 | pending |
| EXECUTE-Step4（20 runs 成功率） | 0 | 2 | pending |

## Iteration 2 — Step 2 反爬實測（trinity）

**結果：8/8 sources ✅ 全部成功（本地 provider 抓實際文章）**
- 8 sources × 1 篇：success 全 true，word_count 848–2690（全 >100），無 paywall，avg ~13.2s
- STAT News 4/4 ✅（1484–2177 words）、Fierce Biotech 4/4 ✅（576–1522 words）— Cloudflare 風險未觸發
- 紀錄檔：`docs/phase1/crawl4ai-p2-antibotsnapshot.md`（新增）
- finding：F-a bioRxiv connect feed 空回應（改走 biorxiv.org API 找 DOI）；F-b SynBioBeta 首頁 promo link 干擾（文章在 `/read/`）
- 未動 code、未 apply DB、未寫入任何資料（範圍錨定遵守）
| VERIFY（smith strict 93） | 0 | 3 | pending |

## Iterations

### Iteration 1 — DISCOVER（morpheus）

**關鍵發現**：
- 🔴 **Supabase project subdomain 全域 NXDOMAIN**（`yihgpsbofjgoxbfypnia.supabase.co` — Cloudflare/Google DoH 皆 Status:3）→ sql/006 無法 apply；`supa()` / `supabase_request()` 會全失敗。**需用戶確認 project 狀態**（可能被刪/搬遷/.env stale）
- 🟢 **5/8 easy sources RSS 直接可達**（STAT/BioPharma Dive/arXiv/Fierce/GEN 皆 200 + 真 XML，pipeline UA 也過）— **推翻 feasibility review 對 STAT/Fierce Cloudflare 的預期**
- 🟡 bioRxiv feed 0-byte（伺服器端壞，但 primary=category_page 不受影響）
- ✅ Nature sitemap 正常；SynBioBeta category page 200 待確認 targets
- sql/006 + sql/003 名稱一致（Endpoints/BioCentury/Science）
- .env 無 CRAWLER_PROVIDER / CRAWLER_ALLOW_CLOUD（Step 1 後需加）

**Neo 策略決策**：P2 核心驗收（Step 2/3/4 反爬 + content_hash + 20 runs）**不依賴 live DB**（純本地 provider 測試）→ 先執行；Step 1（sql/006 apply）標記 BLOCKED 升級用戶。

**Outcome: DISCOVER ✅ → EXECUTE-Step2（反爬實測，純本地）**

### Iteration 2 — EXECUTE-Step2（trinity 反爬實測）

**8/8 easy sources 本地抓取全部成功**（含 STAT/Fierce 額外 4+4 篇，0 失敗）— 推翻 feasibility review 對 STAT/Fierce Cloudflare 的預期；RSS 直達 + 全文抓取皆通。commit `d39db9a`（docs/phase1/crawl4ai-p2-antibotsnapshot.md）

### Iteration 3 — EXECUTE-Step3（trinity content_hash 穩定率）

**初始 40% ❌（2/5 穩定）→ 修復後 100% ✅（5/5）**
- 飄移來源：Nature `_csrf` token / STAT OneTrust cookie modal（+453 words）/ GEN ADVERTISEMENT 行
- 修復（412ad36）：F-1 hash 改用 fit_markdown（word_count 同步）；F-2 normalize 加 boilerplate 排除（CSRF/OneTrust/Nature banner/Sage banner/ADVERTISEMENT + MAX cap 防護）；36 tests pass
- STAT word_count 1484→760（modal 排除後純正文）；hash 基底變更 → DB 既有記錄接受一次不匹配（refresh 循環自然覆蓋）
- commit `412ad36` fix(crawler): F-1+F-2 content_hash stability

**Outcome: Step3 ✅ → EXECUTE-Step4（20 runs 成功率）**

## Circuit Breaker

Consecutive fails: 0/3
Budget: 8%
Status: HEALTHY（Step1 BLOCKED-user，其餘正常）