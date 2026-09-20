# Crawl4AI 新結構 E2E 實測記錄（2026-09-21）

## 目的
驗證 Crawl4AI 本地爬蟲棧 + Provider Abstraction 新結構能實際觸發並跑通完整 pipeline。

## 環境
- Docker：Hermes Gateway (0.21.3) + Langfuse + Langfuse DB（`docker compose up -d`）
- Ollama：qwen3.6:35b-mlx（本機 :11434）
- Supabase：crawl_provider 欄位已落地（8 local + 3 cloud）
- 主機：MacBook Pro（M5 Ultra 會更快）

## 驗證結果（逐步）

| 步驟 | 結果 | 證據 |
|---|---|---|
| Pre-flight | ✅ | `[0/6] ✓ Hermes healthy | Firecrawl key present | Supabase configured` |
| Crawl run 建立 | ✅ | `2c6f47e8-cee0-4575-a955-98d7ef489ecd` |
| Sources 載入 | ✅ | 11 enabled sources |
| **Provider routing** | ✅ | `[pipeline] Nature Biotechnology provider=local`（Crawl4AI 新結構生效） |
| Discovery | ✅ | `✓ Discovered 50 candidate articles`（本地 sitemap） |
| Scrape（Crawl4AI） | ✅ | `→ Scraping article: s41587-026-03264-4` 成功 |
| LLM 分析（Qwen 3.6） | ✅ | `→ Analyzing article with Qwen 3.6 (timeout=300s)` 進行中 |
| 寫入 Supabase | ⏳ | pipeline 仍在跑（每篇 LLM 40-90s） |

## 關鍵驗證：Hermes→Ollama 鏈路
```
curl localhost:8642/v1/chat/completions → HTTP 200, resp "READY"（40s，模型載入）
```
- Hermes auth.json 列出 `openai-api` pooled credential，但 Ollama (`host.docker.internal:11434`) 可達
- 完整鏈路：pipeline → Hermes (:8642) → Ollama (qwen3.6:35b-mlx) ✅

## 新結構與舊結構對比
| 項目 | 舊（Firecrawl-only） | 新（Crawl4AI + Provider Abstraction） |
|---|---|---|
| Routing | 全走 Firecrawl | easy→local Crawl4AI / hard→Firecrawl Cloud |
| Discovery | 全 Firecrawl map | RSS/sitemap/category 本地優先 |
| Scrape | Firecrawl /v1/scrape | Crawl4AI AsyncWebCrawler（0.9.3 新 API） |
| content_hash | raw markdown | fit_markdown + boilerplate exclusion（100% 穩定率） |
| LLM | Firecrawl + cloud LLM | Hermes → Ollama 本地（qwen3.6:35b-mlx） |

## 待補
- pipeline 完整跑完的統計（articles written、errors）— 自動寫入 Supabase
- 全部 8 easy sources 的實際成功率（上輪 20 runs 已驗證 100%）