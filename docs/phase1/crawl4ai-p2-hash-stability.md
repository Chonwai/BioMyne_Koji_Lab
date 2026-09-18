# Crawl4AI P2 — content_hash 穩定率驗證（5 Articles × 2 Fetches）

## Document Status

| Field | Value |
| --- | --- |
| Status | 實測驗證（P2 Step 3 hash 穩定率） |
| Date | 2026-09-19 |
| Type | 實測紀錄（Evidence / Verification，非權威文檔） |
| 上層文檔 | `crawl4ai-migration-overview.md`、`crawl4ai-migration-engineering-spec.md` |
| 環境 | `.venv` Python 3.12.9、crawl4ai==0.9.3、playwright 1.63.0 |
| 驗證標準 | spec Step 5 AC：隨機 5 篇 easy source 文章各抓 2 次，`content_hash` 相同比例 ≥ 80% |

## Executive Summary

針對 5 個 easy sources（混合靜態 + 動態：arXiv / bioRxiv / Nature Biotechnology / STAT News / GEN）各抓 2 次，比較 `_scrape_via_provider.py <url> local` 輸出 JSON 的 `content_hash`（= `hash_markdown(markdown)`）。

**結果：穩定率 2/5 = 40%，未達 80% 標準 ❌。**

- ✅ 穩定：**arXiv**、**bioRxiv**（靜態頁，2 次 hash 完全一致）
- ❌ 飄移：**Nature**（`_csrf` CSRF token 每次 request 變動）、**STAT News**（OneTrust cookie consent modal 隨機被 PruningContentFilter 保留）、**GEN**（動態 `ADVERTISEMENT` / `SCROLL TO CONTINUE WITH CONTENT` 行隨機出現）

**飄移根因**：`hash_markdown()` 只做文字層 normalize（NFC / HTML comment 移除 / 空白壓縮 / lowercase），**無法對抗渲染層動態元素**（CSRF token、cookie modal、動態廣告行）。這些元素由 Crawl4AI 的 `PruningContentFilter(threshold=0.5)` 決定是否保留，而該決定**跨 request 不穩定**。

**fit_markdown 對照實驗**（診斷，未改 code）：改 hash `fit_markdown`（主文區）可修復 Nature（CSRF token 被 fit 過濾），**但無法修復 STAT / GEN** — 兩者的 cookie modal / 廣告行會**隨機**通過 fit 過濾（本次 STAT fit 兩次 word_count 760 vs 1208、GEN fit 兩次 1089 vs 1089 但另一次實驗 1089 vs 1310）。結論：**F-6 建議的「只 hash fit_markdown」只能部分緩解，不足以達到 80%**。

## 1. hash_markdown normalize 現況（`ops/scripts/_pipeline_normalization.py`）

```python
def normalize_markdown_for_hash(markdown: str) -> str:
    normalized = unicodedata.normalize("NFC", markdown or "")   # 1. NFC 正規化
    normalized = re.sub(r"<!--.*?-->", "", normalized, flags=re.DOTALL)  # 2. 移除 HTML comment
    normalized = re.sub(r"[ \t]+", " ", normalized)             # 3. 空白（space/tab）壓縮為單一空格
    normalized = re.sub(r"\r\n?", "\n", normalized)             # 4. CRLF/CR → LF
    normalized = "\n".join(line.strip() for line in normalized.split("\n"))  # 5. 每行 strip
    return normalized.strip().lower()                           # 6. 整體 strip + lowercase

def hash_markdown(markdown: str) -> str:
    return hashlib.sha256(normalize_markdown_for_hash(markdown).encode("utf-8")).hexdigest()
```

| 步驟 | 處理 | 對抗的變異 |
|---|---|---|
| 1 | NFC Unicode 正規化 | 組合字元表示法差異 |
| 2 | 移除 `<!-- -->` comment | 注入的 HTML comment |
| 3 | space/tab → 單一空格 | 縮排 / 對齊空白 |
| 4 | CRLF → LF | Windows / Unix 換行 |
| 5 | 每行 strip | 行首尾空白 |
| 6 | lowercase | 大小寫差異 |

**現況盲點**：以上 6 步全是「字元層」normalize，**不處理任何內容層動態元素**：timestamp、CSRF token、cookie consent modal、廣告行、sidebar 變動內容。spec（`crawl4ai-migration-engineering-spec.md` §F-6）已知此限制，本驗證實測量化其影響。

## 2. 5 篇 × 2 次 hash 比較表

來源選取：依 Step 2 建議混合靜態 + 動態（arXiv 靜態 / bioRxiv 靜態 / Nature 中等 / STAT 動態新聞 / GEN 中等），URL 取自 `crawl4ai-p2-antibotsnapshot.md` 已驗證文章。

| Source | 類型 | run 1 content_hash | run 2 content_hash | 前 8 chars 比對 | word_count (r1/r2) | 穩定 |
|---|---|---|---|---|---|---|
| arXiv q-bio | 靜態 | `b187196904164a98…` | `b187196904164a98…` | 相同 | 848 / 848 | ✅ |
| bioRxiv | 靜態 | `3ddcf15c3de72a2f…` | `3ddcf15c3de72a2f…` | 相同 | 1817 / 1817 | ✅ |
| Nature Biotechnology | 中等 | `85336336143742f2…` | `d79737e067f55e4f…` | 不同 | 2816 / 2816 | ❌ |
| STAT News | 動態 | `592ee78c5b46b3d7…` | `11f612d29ef151a5…` | 不同 | 1484 / 1937 | ❌ |
| GEN | 中等 | `c3bab3e6a50edbc6…` | `0b0ee0198c289498…` | 不同 | 1626 / 1632 | ❌ |

完整 hash（64 chars）：

```
arxiv_1  b187196904164a982a1fd2407684a817477d008dc20672be3e034b3ba1316924
arxiv_2  b187196904164a982a1fd2407684a817477d008dc20672be3e034b3ba1316924
biorxiv_1  3ddcf15c3de72a2f81cef7945b09f0794ea1e9fe5ca89a10b6962a6b887a65a8
biorxiv_2  3ddcf15c3de72a2f81cef7945b09f0794ea1e9fe5ca89a10b6962a6b887a65a8
nature_1   85336336143742f2ed84d6562cdde62eac5064fd5a8af3b7005e2cb6d869943f
nature_2   d79737e067f55e4f2c857ce97c97c406343ec1cc027be7717ba3914e71b908eb
stat_1     592ee78c5b46b3d7d7ae8b8d9730147cdf61de3f88a274d84571cfb216b0890f
stat_2     11f612d29ef151a52f4f9ec1bb9efd697e05ffbd57e9f73ce4df38eb483fe39d
gen_1      c3bab3e6a50edbc6ccaae524fdced3332983ad9933dfd808f05ca4facf40b566
gen_2      0b0ee0198c289498c4dfffa9080d4eb8beae2103d49a9a5c1b76c00d6b266df1
```

## 3. 穩定率 vs 80% 標準

| 指標 | 值 |
|---|---|
| 穩定文章數 | 2 / 5 |
| 穩定率 | **40%** |
| spec 標準 | **≥ 80%** |
| 判定 | **❌ 未達標** |

## 4. 飄移分析

### 4.1 Nature Biotechnology — CSRF token（`_csrf`）

`diff` 僅 1 行差異：

```
87c87
< [ Save article ](https://www.nature.com/articles/s41587-026-03333-8/save-research?_csrf=Ptyl-jJEc59rmMpe2acTsneMyZk0qYSM)
---
> [ Save article ](https://www.nature.com/articles/s41587-026-03333-8/save-research?_csrf=ft2j5LYuVVDRoCMoLzvF1rppi47r2Mnu)
```

- **來源**：Nature 每個 request 頒發新 `_csrf` token，嵌入 Save article 連結
- **特徵**：單一 link、每次必變（100% 飄移）
- **hash_markdown 可否處理**：❌（URL 內容層，非字元層）

### 4.2 STAT News — OneTrust cookie consent modal

`diff` 33 行（`377a378,410`），run 2 多了整個 modal：

```
> ![STAT News](https://cdn.cookielaw.org/logos/static/ot_company_logo.png)
> ## Privacy Preference Center
> When you visit any website, it may store or retrieve information on your browser...
> [More information](https://cookiepedia.co.uk/giving-consent-to-cookies)
> Allow All
> ### Manage Consent Preferences
> #### Strictly Necessary Cookies ... Targeting Cookies ... Performance Cookies ... Functional Cookies
> ### Cookie List ... Apply Cancel ... Reject All Confirm My Choices
> [![Powered by Onetrust](...)](https://www.onetrust.com/products/cookie-consent/)
```

- **來源**：STAT（Boston Globe Media + OneTrust）cookie consent modal，**隨機**被 `PruningContentFilter(threshold=0.5)` 保留或過濾
- **特徵**：約 33 行 boilerplate（~450 words），出現與否跨 request 不穩定。word_count 1484 → 1937（+453）即為 modal
- **hash_markdown 可否處理**：❌（content filter 層的不確定性）

### 4.3 GEN — 動態廣告行

`diff` 2 行（`53a54,55`），run 2 多了：

```
> ADVERTISEMENT
> SCROLL TO CONTINUE WITH CONTENT
```

- **來源**：GEN 站內廣告插槽，**隨機**出現
- **特徵**：動態廣告行，出現與否跨 request 不穩定（另一次實驗中 fit 兩次 word_count 1089 vs 1310 亦為此因）
- **hash_markdown 可否處理**：❌

### 4.4 根因總結

| 飄移類別 | 來源 | 出現模式 | 受影響 source | 現行 normalize 能否處理 |
|---|---|---|---|---|
| 每次必變 | CSRF token（`_csrf`） | 100% 必現 | Nature | ❌ |
| 隨機出現 | OneTrust cookie modal | 有時被 content filter 保留 | STAT | ❌ |
| 隨機出現 | 動態廣告行（ADVERTISEMENT） | 有時被 content filter 保留 | GEN | ❌ |

## 5. fit_markdown 對照實驗（診斷，未改 code）

為驗證 spec F-6 建議「只 hash fit_markdown 主文區」，以 Crawl4AI 0.9.3 正確 API（`markdown.fit_markdown`，`markdown` 回傳 `StringCompatibleMarkdown`，非已棄用 `markdown_v2`）實測 3 個飄移 source：

| Source | full hash (r1/r2) | fit hash (r1/r2) | fit word_count (r1/r2) | fit 穩定？ |
|---|---|---|---|---|
| Nature | 不同 | `5b4b38a0…` = `5b4b38a0…` | 2261 / 2261 | ✅ |
| STAT | 不同 | `6babfcc5…` ≠ `e9caff39…` | 760 / 1208 | ❌ |
| GEN | 不同 | `e2b0b468…` = `e2b0b468…`（本次） | 1089 / 1089 | ⚠️ 隨機 |

> 註：GEN 本次實驗 fit 穩定，但另一次實驗 fit 出現 1089 vs 1310（ADVERTISEMENT 行被 fit 包含）→ **GEN fit 飄移為隨機性**，非穩定。

**結論**：fit_markdown 能移除 Nature 的 CSRF token（其位於頁面側欄/工具列，非主文），但 **STAT 的 cookie modal 與 GEN 的廣告行會隨機通過 fit 過濾** → 「只改 hash fit_markdown」預估穩定率約 3/5 = 60%，**仍低於 80%**。需搭配 finding F-2 的 boilerplate 排除。

## 6. Finding（不自行修改 hash_markdown）

### F-1（spec F-6 已建議，驗證後僅部分有效）：改用 `fit_markdown` 作為 hash 來源

- **證據**：本驗證 5 篇全 markdown hash 穩定率 40%；fit 對照實驗 Nature 修復、STAT/GEN 仍隨機飄移
- **建議**：`LocalCrawl4AIProvider.scrape` 改 hash `markdown.fit_markdown`（0.9.3 API：`markdown` property 回傳 `StringCompatibleMarkdown`，具 `fit_markdown` 屬性；`markdown_v2` 已棄用會 raise AttributeError）。**單獨採用預估 60%，需與 F-2 併用**

### F-2（新增）：normalize 階段排除已知 boilerplate block

- **證據**：STAT OneTrust modal（`Privacy Preference Center` / `cookiepedia.co.uk` / `onetrust.com`）、GEN 廣告行（`ADVERTISEMENT` / `SCROLL TO CONTINUE`）、Nature `_csrf` link
- **建議**：在 `normalize_markdown_for_hash()` 加入 pattern-based 排除（如 `re.sub` 移除含 `_csrf=` 的 URL query、`Privacy Preference Center` 區塊、`ADVERTISEMENT` 行）。**注意**：modal 內容行數不固定（本次 30 行），需以「區塊起訖標記」（`## Privacy Preference Center` → 結尾）而非行數移除
- **風險**：pattern 需隨各 source 演進維護；建議白名單制（只移除已驗證 boilerplate），避免誤刪主文

### F-3（備選，觀察）：提升 PruningContentFilter threshold 或固定 headless 渲染狀態

- **觀察**：STAT modal 與 GEN 廣告行「隨機通過 content filter」本質是渲染結果不確定（cookie banner 出現時機、廣告 slot 填充與否）
- **建議**：若 F-1+F-2 仍不足，可評估 `PruningContentFilter(threshold=0.6+)` 或固定 `--block-media` / 阻擋 OneTrust/GPT 廣告 script（`BrowserConfig` 層），減少渲染層噪音。屬行為變更，需獨立 loop 驗證，**不在本驗證範圍**

### F-4（量化影響）：去重失效的實際成本

- **影響**：hash 飄移 → 同一文章 refresh 時被視為「新內容」→ 重跑 LLM extraction（P1 量測 warm ~5.4 min/篇）→ 重複 article 入庫 + LLM 成本浪費
- **優先序**：P2 上線前應完成 F-1+F-2（去重是 P2A 已上線機制 `sql/004` 的 `content_hash` 唯一鍵基礎，飄移 = 去重閘門失效）

## 7. 重跑方法

```bash
cd /Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji
# 對每篇文章跑 2 次，抽出 content_hash
for i in 1 2; do
  .venv/bin/python3 ops/scripts/_scrape_via_provider.py "<URL>" "local" 2>/dev/null \
    | python3 -c 'import sys,json; print(json.load(sys.stdin).get("content_hash",""))'
done
# 比較兩次輸出（相同 → 穩定；不同 → 飄移）
```

診斷飄移（temp script，不屬 repo）：

```python
# markdown object 暴露 fit_markdown（0.9.3 API）
md_obj = crawl_result.markdown          # StringCompatibleMarkdown（非 string）
fit = md_obj.fit_markdown or ""         # 主文區 markdown
full = str(md_obj)                       # 完整 markdown（與現行 _scrape_via_provider 輸出一致）
```
