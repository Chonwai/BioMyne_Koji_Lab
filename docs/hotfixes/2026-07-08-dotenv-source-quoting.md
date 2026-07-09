# Hotfix Post-Mortem: `.env` 未引號導致 bash source 失敗

**Date:** 2026-07-08
**Severity:** P2 (High)
**Reported by:** 手動管線觸發 (`run_pipeline.sh`)
**Time to Resolution:** ~15 分鐘
**Fix Author:** agent (GitHub Copilot)

## Timeline

- `20:30` 管線觸發後立即失敗，錯誤訊息 `Quantitative: command not found`
- `20:45` 重現確認：`.env` line 22 的 `MAX_ARTICLES_PER_SOURCE_OVERRIDES` 值未加引號
- `20:50` 根因確認：`set -a; source .env; set +a` 時 bash 將包含空格的值解析為多個命令
- `20:55` 修復完成並驗證

## Bug Summary

執行 `bash ops/scripts/run_pipeline.sh` 時，`.env` 被 `source` 載入，因第 22 行的變數值包含空格（`arXiv Quantitative Biology=20`）且未加引號，bash 將 `Quantitative` 解釋為一個獨立的命令名稱，導致 `Quantitative: command not found`。

## Root Cause

`.env` 檔案中的 `MAX_ARTICLES_PER_SOURCE_OVERRIDES` 值未以雙引號包裹：

```bash
# ❌ 錯誤：bash source 時會將 "Quantitative" 當作命令執行
MAX_ARTICLES_PER_SOURCE_OVERRIDES=STAT News=20,Nature Biotechnology=20,Science=20,bioRxiv=20,arXiv Quantitative Biology=20
```

當 `run_pipeline.sh` 執行 `set -a; source "$REPO_ROOT/.env"; set +a` 時，bash 對該行的解析順序為：

1. `MAX_ARTICLES_PER_SOURCE_OVERRIDES=STAT` — 變數賦值（空格前的部分）
2. `News=20,Nature` — 另一變數賦值（bash 吃掉了這部分）
3. `Biotechnology=20,Science=20,bioRxiv=20,arXiv` — 變數賦值
4. **`Quantitative`** — ⛔ 無 `=` 符號，被視為命令名稱 → command not found
5. `Biology=20` — 變數賦值（但執行順序已亂）

這不是管線邏輯的錯誤，而是 **shell `.env` 載入語法**不符合基本規範。

## Fix Applied

在 `.env` 中將該變數值以雙引號包裹：

```bash
# ✅ 正確：bash source 會正確將整個值賦予變數
MAX_ARTICLES_PER_SOURCE_OVERRIDES="STAT News=20,Nature Biotechnology=20,Science=20,bioRxiv=20,arXiv Quantitative Biology=20"
```

Files modified:
- `.env` — 第 22 行加上雙引號
- `.env.example` — 第 18 行加上雙引號（預防性修復，避免下次複製範例時再現相同問題）

## Why It Wasn't Caught Earlier

- 開發階段 `.env` 可能是手動建立的，或者是從 `.env.example` 複製時沒有注意引號
- `.env.example` 本身也存在同樣的未引號問題，但開發者通常不會用 `source` 加載 `.env.example`
- 之前的管線執行可能因為該變數未被實際使用（或使用不同方式加載）而未觸發

## Prevention Actions

- [ ] 同步修復 `.env.example` 的相同問題，確保複製範例不會產生同樣的 bug — assigned to: team
- [ ] 考慮在 pipeline 前增加 `.env` 格式的靜態檢查（如 `bash -n .env` 或 key-value 引號完整性檢查）— tracked in: next sprint
- [ ] 在所有 shell 腳本中統一 `.env` 加載模式，確保所有包含空格的值都妥善引號處理 — tracked in: next sprint
