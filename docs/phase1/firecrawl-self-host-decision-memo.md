# BioMyne Koji Firecrawl Self-Host 決策備忘錄

> 版本：v1.0
> 日期：2026-07-08
> 狀態：研究完成，等待 Founder / Engineering Owner 決策
> 範疇：research + planning only，不含開發
> 品質模式：strict（93+）
> 研究方法：Firecrawl 官方文件 / 官方 repo 一手交叉驗證 + Jarvis Deep Research + Koji 現況設計比對
> 主要問題：Koji 是否應從 Firecrawl Cloud 轉向 self-host Firecrawl？如果不是現在，何時、以什麼模式最合理？

---

## 1. 結論先講

### 核心結論

**Firecrawl 確實可以 self-host，但現在不建議 Koji 直接全面轉向 self-host。**

更精確地說：

1. **技術上可行**：官方 repo 明確提供 `SELF_HOST.md`、`docker-compose.yaml`、Kubernetes/Helm 範例，代表 self-host 不是社群 hack，而是官方支援的 open-source 部署路徑。
2. **功能上不等價**：官方文件明寫 self-host **沒有 Fire-engine**，且 cloud 才有 `Agent`、`Browser sandbox`、`Actions`、`Enhanced proxies`、`Proxy rotations`、`Dashboard`、enterprise features。這表示 self-host 不能被視為「免費版 Firecrawl Cloud」。
3. **經濟上未必更便宜**：self-host 解除的是 monthly credits 限制，但同時引入機器、proxy、CAPTCHA、queue、browser、維運、升級、故障排查與成功率波動的成本。對 11 個 sources 目前幾乎不划算；對 50 個 sources 通常仍不夠有說服力；對 200 個 sources 才開始可能進入值得評估的區間。
4. **對 Koji 最合理的中期方向是 hybrid，而不是 wholesale replacement**：
   - 高價值、難爬、反爬強、需要高穩定性的來源繼續走 cloud
   - 低價值、易爬、可容忍較高失敗率的來源，未來可用 self-host PoC 驗證
   - 在切換前，必須先做 provider abstraction，避免目前對 cloud contract 的硬綁定

### 總體推薦

| Option                                                                        |  建議度  | 結論                     |
| ----------------------------------------------------------------------------- | :------: | ------------------------ |
| Option A: 繼續用 Firecrawl Cloud + 優化 discovery / refresh / dedupe / budget |  **高**  | **現在的預設最佳路徑**   |
| Option B: 混合模式（cloud + self-host fallback / low-value sources）          | **中高** | **中期最值得研究的方向** |
| Option C: 完全轉向 self-host                                                  |  **低**  | **現在不建議**           |

---

## 2. 官方已驗證事實

以下事項已由 Firecrawl 官方文件或官方 repo 一手驗證：

### 2.1 Open Source vs Cloud 的官方差異

官方 `Open Source vs Cloud` 頁面對功能差異寫得很清楚：

| 能力                | Open Source / Self-host | Cloud |
| ------------------- | :---------------------: | :---: |
| Scrape              |            ✔            |   ✔   |
| Crawl               |            ✔            |   ✔   |
| Map                 |            ✔            |   ✔   |
| Search              |            ✔            |   ✔   |
| Batch Scrape        |            ✔            |   ✔   |
| Extract / JSON mode |            ✔            |   ✔   |
| Change tracking     |            ✔            |   ✔   |
| SDKs                |            ✔            |   ✔   |
| Agent               |            ✘            |   ✔   |
| Browser sandbox     |            ✘            |   ✔   |
| Actions             |            ✘            |   ✔   |
| Enhanced proxies    |            ✘            |   ✔   |
| Proxy rotations     |            ✘            |   ✔   |
| Dashboard           |            ✘            |   ✔   |
| Enterprise features |            ✘            |   ✔   |

### 2.2 Self-host 官方限制

官方 `SELF_HOST.md` 明寫：

1. **Limited Access to Fire-engine**
   - self-host 沒有 Fire-engine
   - 這意味著對 IP blocks、robot detection 等進階能力不應預期與 cloud 等價
2. **Manual Configuration Required**
   - 超出 basic fetch / Playwright 的能力需要手動配置 `.env`
3. **Supabase 目前無法在 self-host instance 中配置**
   - 官方 troubleshooting 明寫：`Right now it's not possible to configure Supabase in self-hosted instances.`
   - 這不會阻止 Koji 自己使用 Supabase，但代表你不能假設 Firecrawl self-host 內部會直接沿用 cloud 的 Supabase / auth / event logging 模式
4. **Self-host SDK 使用時 API key 可選**
   - 官方 troubleshooting 明寫：SDK 在 self-host 模式下 API keys 是 optional；cloud 才需要 `FIRECRAWL_API_KEY`
5. **部分 AI features 依賴外部 LLM provider**
   - JSON format on scrape
   - `/extract`
   - summary format
   - branding format
   - change tracking format
     這些都要求 `OPENAI_API_KEY` 或替代 LLM provider / `OLLAMA_BASE_URL`

### 2.3 官方自架堆疊元件

來自 `docker-compose.yaml` 與 Helm README 的官方元件：

**Compose / 單機最小堆疊**

- `api`
- `playwright-service`
- `redis`
- `rabbitmq`
- `nuq-postgres`
- `foundationdb`（experimental queue backend，可選）

**Helm / 生產型堆疊**

- `api`
- `worker`
- `extract-worker`
- `nuq-worker`
- `nuq-prefetch-worker`
- `cclog-worker`
- `playwright-service`
- `redis`
- `nuq-postgres`
- `rabbitmq`

這證明 self-host 在 production 視角下不是「一個 container」，而是一套 crawler platform。

### 2.4 Cloud 價格與 credit 規則

官方 `pricing.md` 已確認：

| 項目          | 規則                                    |
| ------------- | --------------------------------------- |
| Free          | 1,000 credits / month                   |
| Hobby         | 5,000 credits / month, $19 / month      |
| Standard      | 100,000 credits / month, $99 / month    |
| Growth        | 500,000 credits / month, $399 / month   |
| Scale         | 1,000,000 credits / month, $749 / month |
| Map           | **1 credit per call**                   |
| Scrape        | 1 credit per page                       |
| Crawl         | 1 credit per page                       |
| Search        | 2 credits per 10 results                |
| Interact      | 2 credits per browser minute            |
| JSON format   | +4 credits per page                     |
| Enhanced Mode | +4 credits per page                     |

這點非常重要：**Map 的成本本來就不高，真正會放大的是 scrape 量與進階功能。**

---

## 3. 對 Koji 的真正意義

### 3.1 使用者的直覺 vs 實際情況

使用者的直覺是：

> 如果 self-host Firecrawl，就不用被 online 版 credits 限制住。

這個直覺**只有一半是對的**。

### 3.2 真正發生的事情

如果轉 self-host，你解除的是：

- Firecrawl monthly credits ceiling
- Firecrawl cloud billing API / plan boundary

但你同時得到的是：

- 自己的 API / worker / browser stack
- 自己的 Redis / RabbitMQ / Postgres
- 自己的 proxy strategy
- 自己的 anti-bot 成功率問題
- 自己的 queue jam / crash / restart / retry / observability 問題
- 自己的升級、版本相容與事故處理責任

所以 self-host 並不是把成本消失，而是把成本形態從：

- `按次付費`

轉成：

- `固定 infra + 變動 proxy / CAPTCHA + 維運 / 失敗率風險`

### 3.3 對 Koji 目前階段的判斷

Koji 現在只有 11 個 curated sources。

在這個量級下，Koji 真正需要優先處理的仍然是：

- discovery signal quality
- cursor-first discovery
- URL normalization
- content hash skip
- refresh lane
- per-source routing
- budget mode

也就是說，**Koji 還沒走到「credits 爆炸是頭號問題」的階段。**

現在更可能發生的是：

- 你先把 infra complexity 引進來
- 卻還沒把 cloud 路線上最值錢的 dedupe / refresh / signal engineering 做完

這會讓團隊太早把時間花在 crawler platform engineering，而不是情報質量工程。

---

## 4. Self-host 架構分析

### 4.1 最小可行 PoC（MVP）

如果只是驗證「Koji 是否能用 self-host Firecrawl 處理一些低風險來源」，最小堆疊可以是：

| 元件                 |     是否需要     | 角色                                        |
| -------------------- | :--------------: | ------------------------------------------- |
| `api`                |        是        | Firecrawl API server                        |
| `playwright-service` |        是        | 渲染、互動、JS 頁面處理                     |
| `redis`              |        是        | rate limit / queue / coordination           |
| `rabbitmq`           |        是        | job transport                               |
| `nuq-postgres`       |        是        | queue / persistence state                   |
| Proxy                | 否（PoC 可不接） | 先挑 easy sources 測試                      |
| 外部 LLM provider    | 視 feature 而定  | 若要 JSON / changeTracking / extract 則需要 |
| Monitoring           |    最少 logs     | PoC 可簡化，但仍要有基本可觀測性            |

### 4.2 Production-grade 自架版本

若目標是「長期替代 cloud 的核心 scrape 能力」，production-grade 不能只跑 compose。至少應有：

| 區塊             | 需要內容                                                                        |
| ---------------- | ------------------------------------------------------------------------------- |
| API 層           | `api` service + auth / ingress / rate limits                                    |
| Browser 層       | `playwright-service` + browser pool sizing                                      |
| Worker 層        | `worker`, `extract-worker`, `nuq-worker`, `nuq-prefetch-worker`, `cclog-worker` |
| Queue 層         | `redis` + `rabbitmq`                                                            |
| State 層         | `nuq-postgres`（或實驗性 `foundationdb`）                                       |
| Proxy 層         | residential / datacenter proxy 配置與熔斷                                       |
| Observability    | logs, metrics, queue depth, job age, success rate, browser crash rate           |
| Secrets 管理     | proxy creds, optional LLM keys, admin panel auth                                |
| 備份 / retention | queue / state / artifact lifecycle                                              |

### 4.3 官方 compose 顯示的資源訊號

官方 `docker-compose.yaml` 給出的 compose limits 本身就是一個很有價值的信號：

| 服務                 | 官方 compose limits |
| -------------------- | ------------------- |
| `playwright-service` | 2 CPU / 4 GB RAM    |
| `api`                | 4 CPU / 8 GB RAM    |

這代表官方預設就不是把 self-host 當成「超輕量、隨便一台小機器就很穩」的服務。

實務上，若你要單機跑一個像樣的 PoC，**6 CPU / 12 GB RAM 級別** 比較像可信起點，而不是想像中的超低成本 sidecar。

---

## 5. Koji 現有設計假設會被打破的地方

Koji 現在明顯是 **cloud-contract-first** 的設計，而不是 provider-agnostic 設計。

### 5.1 目前 repo 的硬綁定點

| 現在假設                                                | 位置                                               |          self-host 後是否仍成立           |
| ------------------------------------------------------- | -------------------------------------------------- | :---------------------------------------: |
| `FIRECRAWL_KEY` 一定存在                                | `.env.example`, scripts                            |                 ❌ 不一定                 |
| base URL 固定是 `api.firecrawl.dev`                     | `_discover_article_urls.py`, `_scrape_markdown.py` |                 ❌ 不成立                 |
| `/v1/scrape`、`/v2/map` cloud semantics 不變            | helpers                                            |                ❌ 不應假設                |
| `/team/credit-usage` 有意義                             | runbook / P2 plan                                  |  ❌ self-host 無 cloud billing semantics  |
| team queue / concurrency 是官方產品 contract            | cloud APIs                                         |       ❌ self-host queue 是你自己養       |
| Search 品質與 backend 一樣                              | current mental model                               |   ❌ self-host 可能走 Google / SearXNG    |
| changeTracking / monitor / Slack / dashboard 可直接沿用 | planning assumptions                               | ❌ 至少部分是 cloud-only 或 parity 未保證 |

### 5.2 對 Koji 的必要抽象層

如果未來真的要碰 self-host，Koji **必須先做 provider abstraction**。

至少要抽成一個 provider contract，明確定義：

| 能力                            | 說明                                       |
| ------------------------------- | ------------------------------------------ |
| `base_url`                      | cloud 或 self-host API base URL            |
| `auth_mode`                     | bearer key / optional auth / internal auth |
| `supports_team_billing`         | 是否支援 credits / team billing API        |
| `supports_search`               | Search 是否可用且可信                      |
| `supports_monitor`              | Monitor 是否可用                           |
| `supports_browser_features`     | Browser sandbox / actions 類能力           |
| `supports_change_tracking_json` | 結構化 diff 是否可用                       |
| `supports_enhanced_proxy`       | 是否有 vendor-managed proxy layer          |
| `healthcheck_contract`          | 怎樣算 healthy                             |
| `retry_policy`                  | provider-specific retry / backoff          |
| `per_source_routing_policy`     | 哪些來源走哪個 provider                    |

**在沒有這個 abstraction 前，不建議碰 self-host。**

---

## 6. 成本模型比較

### 6.1 Cloud 成本（對 Koji 規模）

用 Koji 目前已建模的 11-source 情境：

| 情境             | 月 Credits | 比較合適的 plan                         |
| ---------------- | :--------: | --------------------------------------- |
| 現況（P0/P1 後） |   ~4,830   | Hobby 幾乎貼頂；Standard 有充足 buffer  |
| P2A              |   ~3,044   | Hobby 可跑但 buffer 不大；Standard 最穩 |
| P2A+B            |   ~3,944   | Hobby 可跑但風險高；Standard 最穩       |
| P2A+B+C          |   ~2,022   | Hobby 可行                              |

結論：

- **11-source 量級根本還不到被 Standard plan 卡死的程度**
- 你甚至還在「Hobby 幾乎可行 / Standard 很從容」的區間

### 6.2 Self-host 固定成本

根據研究與官方 compose/helm 架構，self-host 的成本至少包含：

| 類型              | 內容                           |
| ----------------- | ------------------------------ |
| Compute           | 單機 Docker / VM / K8s cluster |
| Queue / DB        | Redis, RabbitMQ, Postgres      |
| Browser resources | Playwright service CPU / RAM   |
| Proxy             | datacenter / residential proxy |
| CAPTCHA           | solver（若來源需要）           |
| Observability     | metrics, logging, alerting     |
| Ops time          | 升級、事故、排障、回退         |

### 6.3 重要經濟判斷

| 問題                                                   | 結論                                                 |
| ------------------------------------------------------ | ---------------------------------------------------- |
| 「self-host 一定比較便宜嗎？」                         | **不一定**                                           |
| 「11 sources 值得為了省 credits 自架嗎？」             | **通常不值得**                                       |
| 「如果 Mac Studio 已是 sunk cost，是否會變得更合理？」 | **會稍微更合理，但 proxy / 失敗率 / 維運仍是實成本** |
| 「若 sources 擴到 200，是否開始值得？」                | **有可能，但前提很多**                               |

### 6.4 11 / 50 / 200 sources 的方案判斷

| 規模            | 雲端 Firecrawl                        | self-host Firecrawl                 | 我的判斷                                           |
| --------------- | ------------------------------------- | ----------------------------------- | -------------------------------------------------- |
| **11 sources**  | 非常合理                              | 技術可行但經濟性差                  | **選 cloud**                                       |
| **50 sources**  | 仍多半合理                            | 可開始做 hybrid PoC                 | **選 cloud 或保守 hybrid**                         |
| **200 sources** | 可能逼近更高 plan /需要更嚴格成本治理 | 若 sources 大多易爬，才可能有經濟性 | **可研究 hybrid，極少數情況才考慮 full self-host** |

---

## 7. 風險矩陣

### 7.1 技術風險

| 風險                          | cloud                   | self-host                    | 對 Koji 影響 |
| ----------------------------- | ----------------------- | ---------------------------- | ------------ |
| Anti-bot / IP block           | vendor absorb 一部分    | 你自己處理                   | 高           |
| Browser crash / cold start    | vendor absorb           | 你自己處理                   | 中高         |
| Queue backlog / stuck jobs    | vendor product contract | 你自己維運                   | 高           |
| Search quality                | vendor-managed          | 取決於 Google / SearXNG 配法 | 中           |
| Feature parity drift          | 小                      | 大                           | 高           |
| Screenshot / artifact parity  | 高                      | 不宜直接假設                 | 中           |
| Monitor / notification parity | 高                      | 不宜直接假設                 | 中           |

### 7.2 法律與合規風險

| 風險             | 說明                                                                 |
| ---------------- | -------------------------------------------------------------------- |
| Robots.txt / ToS | self-host 不會降低義務，反而讓你自己成為直接操作者                   |
| AGPL-3.0         | 若你修改並對外提供 network service，需做 license / compliance review |
| Data residency   | self-host 是優勢，但前提是你真的需要這個合規價值                     |
| IP reputation    | 來源封鎖與風險會更直接落到你的 infra 與網段上                        |

### 7.3 營運風險

| 風險     | 說明                                                           |
| -------- | -------------------------------------------------------------- |
| 監控不足 | 沒有 queue depth / success-rate / browser crash 監控就會非常盲 |
| 升級成本 | Firecrawl release 頻繁，自架要自己驗證相容性                   |
| 隱性成本 | 故障排除與人工時間經常比 VM 帳單更昂貴                         |

---

## 8. Option A / B / C 決策比較

### Option A：繼續用 Cloud Firecrawl

**適用條件**

- 11–50 sources
- 更重視穩定性與低維運
- 還沒有證明 credits 真的是主瓶頸

**優點**

- 上線快
- feature 完整
- anti-bot / proxy / browser / dashboard 已託管
- 對 Koji 現有架構幾乎零改動

**缺點**

- credits 是顯性成本
- vendor dependency 高

**推薦度**：**高**

### Option B：混合模式（推薦的中期方向）

**做法**

- 高價值 / 難爬 / 反爬強的來源留在 cloud
- 低價值 / 易爬 / 可容忍較高失敗率的來源做 self-host PoC
- 對 provider 做 source-level routing

**優點**

- 風險可切分
- 成本可觀測
- 有 fallback，不是一次 all-in
- 可逐步驗證 economics 與成功率

**缺點**

- 需要 provider abstraction
- 增加系統複雜度
- 會引入**雙 provider 維護稅**：
  - 兩套 provider capability matrix
  - source routing 規則與測試矩陣
  - 兩套 success-rate / alerting / rollback 思維
  - 雲端與 self-host 之間的 parity drift 管理

**推薦度**：**中高**

### Option C：完全轉向 self-host

**做法**

- 把 Koji 的 Firecrawl 依賴全部遷到自架堆疊

**問題**

- 需要自養 crawler platform
- feature parity 不完整
- 失敗率與 anti-bot 風險上升
- 不一定更便宜

**推薦度**：**低**

---

## 9. 建議路線圖（研究後規劃，不是現在開發）

### Phase S0：Decision Only（現在）

目標：只做 research 與共識，不開發。

輸出：

- 本 decision memo
- 是否批准進入 self-host PoC planning

### Phase S1：Provider Abstraction Planning

若要往 hybrid / self-host 走，第一步不是部署 Firecrawl，而是先設計 Koji provider abstraction。

**輸出**

- provider interface 設計草圖
- cloud/self-host capability matrix 對應到 Koji pipeline 的欄位
- source-level routing policy 草案

### Phase S2：Self-host PoC（只選 easy sources）

**PoC 範圍建議**

- 只選 5–10 個 easy-mode sources
- 不碰 screenshot / agent / browser sandbox / dashboard-only 能力
- 只驗證 `map + scrape(markdown) + basic change detection`
- 保留 cloud 作為對照組

**成功標準**

- 連續 2 週成功率 >= 95%
- 對照 cloud 的內容完整度差距可接受
- 每週人工介入 <= 1–2 次
- Queue / browser / retry 沒有持續性失控
- projected 50-source monthly total cost 對 cloud 有明顯優勢（至少 30–40%）

### Phase S3：Hybrid Pilot

在 PoC 成功後，才考慮：

- low-value sources → self-host
- high-value / hard sources → cloud

### Phase S4：Re-evaluate Full Migration

只有在以下條件全部成立時，才討論 full self-host：

- 70–80% 以上 sources 經證明屬於 easy-mode
- provider abstraction 已穩定
- monitoring / rollback / routing 已完整
- 經濟模型明顯優於 cloud
- 團隊願意長期維運這套平台

---

## 10. 需要新增的 infra / secrets / monitoring（若未來進入 PoC）

### 10.1 Infra

- Firecrawl `api`
- `playwright-service`
- `redis`
- `rabbitmq`
- `nuq-postgres`
- optional `SearXNG`
- optional object storage / MinIO（若未來需要 artifact）

### 10.2 Secrets / Config

- self-host base URL
- optional auth mode
- proxy credentials
- optional CAPTCHA solver credentials
- optional LLM provider credentials（若用 JSON / changeTracking / extract）
- admin / queue panel secret（`BULL_AUTH_KEY`）

### 10.3 Monitoring

至少要有：

- queue depth
- active jobs
- waiting jobs
- scrape success rate
- browser crash rate
- retry count
- per-source failure rate
- proxy bandwidth / proxy error rate
- stale job age
- time-to-first-byte / latency distributions

---

## 11. 最終建議

### 我對 Koji 的正式建議

**現在不要把 Koji 直接改成 self-host Firecrawl。**

更好的順序是：

1. 先把 cloud 路線上的高 ROI 事情做完：
   - cursor-first discovery
   - URL normalization
   - content hash skip
   - refresh lane
   - category rotation
   - budget modes
2. 如果之後 sources 擴張到 50–200，且 credits 真的開始成為明顯瓶頸，再做 self-host PoC
3. 若要碰 self-host，**先做 provider abstraction，再做 PoC，再做 hybrid，不要直接 full replacement**

### 最關鍵的一句話

**self-host 不是「免 credits 的 Firecrawl Cloud」；它是把 vendor bill 轉成 internal platform bill。**

---

## 12. 批准前問題

如果你要把這條 research 線繼續往前推，建議先回答以下問題：

1. Koji 是否真的有明確的 data residency / compliance 驅動，足以 justify 自架？
2. 你要解的是「credits 成本」，還是「未來 sources 擴張時的可控性」？這兩者的解法不同。
3. 當 sources 擴到 50 或 200 時，你是否願意把 crawler infra 當成一個長期產品能力來養？
4. 若要做 PoC，哪些 5–10 個 sources 可以被定義為 easy-mode sources？
5. 是否接受在 self-host 路線上先投入 provider abstraction，而不是先急著部署 compose？

### 法務與授權補充說明

Firecrawl open-source 採用 `AGPL-3.0`。本文件不是法律意見，但在決策層至少要分清兩種情境：

- **純內部使用 / 內部 PoC**：通常比對外提供 network service 的風險低得多
- **修改後對外提供服務或讓外部使用者直接透過 network interaction 使用**：需要做更正式的 license / compliance review

因此，若未來只是 Koji 內部自用 PoC，法務壓力通常較小；若未來打算把自架 Firecrawl 變成更通用的對外服務，則必須先做授權與合規審查。

---

## 13. 與 Koji 現有規劃文件的關係

這份文件是 [p2-crawl-strategy-planning.md](/Users/chonwai/Desktop/BioMyne_Intelligence_Operating_Layer/BiomyneKoji/biomyne-koji/docs/phase1/p2-crawl-strategy-planning.md) 的補充 decision memo。

兩份文件的角色分工：

| 文件                                   | 角色                                              |
| -------------------------------------- | ------------------------------------------------- |
| `p2-crawl-strategy-planning.md`        | cloud-first P2 crawler evolution 的主規劃文件     |
| `firecrawl-self-host-decision-memo.md` | 是否要引入 self-host Firecrawl 的策略判斷與路線圖 |

目前的總體建議是：

- 以 `p2-crawl-strategy-planning.md` 為主線
- 以本文件作為未來是否進入 self-host / hybrid PoC 的 gating 依據

### 何時重新評估 self-host

建議只有在以下條件同時接近成立時，才正式打開 self-host / hybrid PoC：

1. `p2-crawl-strategy-planning.md` 中的 P2A 已完成，且 4 週後仍無法把雲端路線的 signal efficiency 拉到可接受水位
2. 真實月度雲端成本開始逼近升級邊界，而不是停留在 Hobby / Standard 的舒適區
3. 新增 sources 的結構多數是 public / feed-friendly / category-friendly，而不是高強度 anti-bot 站點
4. 團隊接受把 crawler infra 視為長期維運能力，而非一次性 side project

---

## 14. 來源與信心等級

### 一手官方來源

- Firecrawl 官方 docs：Open Source vs Cloud、Self-hosting、Queue Status、Monitoring、Pricing
- Firecrawl 官方 repo：`README.md`、`SELF_HOST.md`、`docker-compose.yaml`、Helm README

### 二手 / 市場資訊

- self-host 經濟模型、proxy / CAPTCHA 市場成本、雲 VM 成本帶來的是**方向性判斷**，不是不可變常數
- 因此文件中的成本比較應視為 planning estimate，不是採購報價

### 信心等級總結

| 題目                                   |          信心          |
| -------------------------------------- | :--------------------: |
| Firecrawl 可以 self-host               |           高           |
| self-host 與 cloud 功能不等價          |           高           |
| 11 sources 不值得現在 full self-host   |           高           |
| hybrid 是中期最合理方向                |           高           |
| 50 sources 時可以開始 PoC              |          中高          |
| 200 sources 時 full self-host 可能合理 |           中           |
| self-host 一定更便宜                   | 低（我不認同這個命題） |
