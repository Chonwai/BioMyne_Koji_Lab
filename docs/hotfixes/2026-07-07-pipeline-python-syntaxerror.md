# Hotfix Post-Mortem: 管線 LLM 分析步驟 Python SyntaxError

**Date:** 2026-07-07
**Severity:** P1 (Critical)
**Reported by:** 手動管線觸發
**Time to Resolution:** ~25 minutes
**Fix Author:** agent (GitHub Copilot)

## Timeline
- `16:40` 管線首次運行，STAT News scraping 成功，但在分析步驟失敗
- `16:45` 問題確認，開始重現與根因分析
- `16:53` 根因確定：bash 3.2 `$(...)` 內 `"..."` + `<<<` + 多行 `-c` 觸發 parsing bug
- `16:55` 修復部署：提取 Python 代碼到獨立 `_build_llm_request.py`，改用 `printf | python3 script.py`
- `16:55` 修復驗證：管線成功處理 3 個來源、提取 9 篇文章、寫入 Supabase

## Bug Summary
`run_pipeline.sh` 在 LLM 分析步驟（Step 4）失敗，拋出 5 個 Python `SyntaxError: invalid syntax`。根因為 bash 3.2.57 (macOS 內建) 將多行 `python3 -c "..."` 代碼錯誤地分割為多個獨立命令，每個只包含字典的部分內容。

## Root Cause
**bash 3.2.57 的 parsing bug**：當 `$(python3 -c "多行代碼")` 嵌套在 `-d "$(...)"` 內部，且結合 `<<<` here-string 時，多行字串中的換行符被錯誤解釋為命令分隔符。

Bash trace (`bash -x`) 清楚顯示每個字典鍵值對被分派為獨立 `python3 -c` 調用：
```
+++ python3 -c '...model...'
+++ python3 -c '...messages...'
+++ python3 -c '...max_tokens...'
+++ python3 -c '...temperature...'
```

每個片段缺少 `{` 開括號，導致 `SyntaxError`。

## Fix Applied
將 inline Python JSON 構建代碼提取到獨立腳本 `ops/scripts/_build_llm_request.py`，管線改用 `printf '%s' "$PROMPT" | python3 "$SCRIPT_DIR/_build_llm_request.py"` 傳遞輸入，徹底避免 bash 3.2 的 parsing bug。

Files modified:
- `ops/scripts/run_pipeline.sh` — 將 `$(python3 -c "多行" <<< "$PROMPT")` 替換為 `printf ... | python3 _build_llm_request.py`
- `ops/scripts/_build_llm_request.py` — 新建，讀取 stdin prompt + env MODEL，輸出 JSON

## Why It Wasn't Caught Earlier
- 開發環境使用 fish/zsh shell，這些 shell 沒有此 bug
- 管線腳本明確使用 `#!/usr/bin/env bash`，指向 macOS 內建 bash 3.2
- Bash 3.2 的 `$(...)` + `"..."` + `<<<` 組合 bug 是特定版本的邊緣情況

## Prevention Actions
- [ ] 考慮在管線腳本頂部添加 bash 版本檢查，建議使用 Homebrew bash 5+ — assigned to: team
- [ ] 將其他多行 `python3 -c` 調用也評估是否需要重構為獨立腳本 — tracked in: 下個 Sprint
- [ ] 在 smoke test 中添加管線端到端測試 — assigned to: team
