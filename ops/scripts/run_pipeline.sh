#!/usr/bin/env bash
# ============================================================
# BioMyne Koji — Manual Intelligence Pipeline Trigger
# Usage: bash ops/scripts/run_pipeline.sh
#
# Flow:
#   Supabase sources → Firecrawl scrape → Qwen 3.6 analyze
#   → Supabase articles/entities → Terminal digest
# ============================================================
set -e

# ── Config (override via .env or environment) ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load .env if present
if [ -f "$REPO_ROOT/.env" ]; then
  set -a; source "$REPO_ROOT/.env"; set +a
fi

HERMES_URL="${HERMES_URL:-http://localhost:8642}"
HERMES_KEY="${HERMES_KEY:-koji-phase1-local}"
FIRECRAWL_KEY="${FIRECRAWL_KEY:-}"
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"
MODEL="${OLLAMA_MODEL_TAG:-qwen3.6:35b-mlx}"
MAX_ARTICLES_PER_SOURCE="${MAX_ARTICLES_PER_SOURCE:-15}"
MAX_ARTICLES_PER_SOURCE_OVERRIDES="${MAX_ARTICLES_PER_SOURCE_OVERRIDES:-}"
MIN_WORDS_FOR_LLM="${MIN_WORDS_FOR_LLM:-300}"
LLM_TIMEOUT="${LLM_TIMEOUT:-180}"
LLM_MAX_TOKENS="${LLM_MAX_TOKENS:-4096}"
DELIVERY_CHANNEL="${DELIVERY_CHANNEL:-manual_terminal}"
RUN_ID=""
RUN_START=""
SOURCE_COUNT=0
TOTAL_ARTICLES=0
ERRORS=0
FINALIZED=0

# ── Colors ──
BOLD='\033[1m'; CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

articles_limit_for_source() {
  local source_name="$1"
  local default_limit="$MAX_ARTICLES_PER_SOURCE"

  if [ -z "$MAX_ARTICLES_PER_SOURCE_OVERRIDES" ]; then
    printf '%s\n' "$default_limit"
    return
  fi

  local override
  override=$(SOURCE_NAME="$source_name" DEFAULT_LIMIT="$default_limit" MAX_ARTICLES_PER_SOURCE_OVERRIDES="$MAX_ARTICLES_PER_SOURCE_OVERRIDES" python3 <<'PY'
import re
import os

source_name = os.environ["SOURCE_NAME"].strip().lower()
default_limit = os.environ["DEFAULT_LIMIT"]
raw = os.environ.get("MAX_ARTICLES_PER_SOURCE_OVERRIDES", "").strip()

if not raw:
    print(default_limit)
    raise SystemExit(0)

for entry in raw.split(','):
    if '=' not in entry:
        continue
    key, value = entry.split('=', 1)
    normalized_key = re.sub(r'[^a-z0-9]+', '', key.lower())
    normalized_source = re.sub(r'[^a-z0-9]+', '', source_name)
    if normalized_key == normalized_source and value.strip().isdigit():
        print(value.strip())
        raise SystemExit(0)

print(default_limit)
PY
)

  if [ -z "$override" ]; then
    override="$default_limit"
  fi
  printf '%s\n' "$override"
}

supa() {
  # Supabase REST helper: supa GET /rest/v1/sources?select=name
  # or: supa POST /rest/v1/articles '{"field":"value"}'
  local method="$1" path="$2" body="${3:-}"
  local url="${SUPABASE_URL}${path}"
  local header_auth="Authorization: Bearer ${SUPABASE_KEY}"
  local header_api="apikey: ${SUPABASE_KEY}"
  
  if [ "$method" = "POST" ] || [ "$method" = "PATCH" ]; then
    curl -s --max-time 15 -X "$method" "$url" \
      -H "$header_api" -H "$header_auth" \
      -H "Content-Type: application/json" \
      -H "Prefer: return=representation" \
      -d "$body" 2>/dev/null
  else
    curl -s --max-time 15 -X "$method" "$url" \
      -H "$header_api" -H "$header_auth" 2>/dev/null
  fi
}

finalize_incomplete_run() {
  local exit_code="$?"
  if [ -z "$RUN_ID" ] || [ "$FINALIZED" -eq 1 ]; then
    return
  fi

  set +e
  local run_end status note
  run_end=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  if [ "$exit_code" -eq 0 ]; then
    if [ "$ERRORS" -gt 0 ]; then
      status="partial_success"
      note="Manual pipeline run finished via EXIT trap."
    else
      status="success"
      note="Manual pipeline run finished via EXIT trap."
    fi
  else
    status="failed"
    note="Manual pipeline run exited early with code $exit_code."
  fi

  supa PATCH "/rest/v1/crawl_runs?id=eq.$RUN_ID" "{
    \"completed_at\": \"$run_end\",
    \"status\": \"$status\",
    \"article_count\": $TOTAL_ARTICLES,
    \"error_count\": $ERRORS,
    \"notes\": \"$note\"
  }" > /dev/null 2>&1 || true
}

trap finalize_incomplete_run EXIT

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║   BioMyne Koji — Intelligence Pipeline (Manual Run)  ║"
echo "║   $(date '+%Y-%m-%d %H:%M:%S')                               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Step 0: Pre-flight checks ──
echo -e "\n${CYAN}[0/6] Pre-flight checks...${NC}"

if [ -z "$FIRECRAWL_KEY" ]; then
  echo -e "${RED}✗ FIRECRAWL_KEY not set. Check your .env file.${NC}"; exit 1
fi
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
  echo -e "${RED}✗ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set.${NC}"; exit 1
fi

# Check Hermes health
if ! curl -s --max-time 5 "$HERMES_URL/health" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='ok' else 1)" 2>/dev/null; then
  echo -e "${RED}✗ Hermes Gateway not reachable at $HERMES_URL${NC}"; exit 1
fi
echo -e "${GREEN}✓${NC} Hermes healthy | Firecrawl key present | Supabase configured"

# ── Step 1: Create crawl run ──
echo -e "\n${CYAN}[1/6] Creating crawl run...${NC}"
RUN_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
RUN_START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

supa POST /rest/v1/crawl_runs "{
  \"id\": \"$RUN_ID\",
  \"run_type\": \"manual\",
  \"started_at\": \"$RUN_START\",
  \"status\": \"in_progress\",
  \"source_count\": 0,
  \"article_count\": 0,
  \"error_count\": 0
}" > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Crawl run created: $RUN_ID"

# ── Step 2: Fetch sources from Supabase ──
echo -e "\n${CYAN}[2/6] Fetching sources from Supabase...${NC}"
SOURCES_JSON=$(supa GET "/rest/v1/sources?select=id,name,url,domain,extraction_mode&enabled=eq.true" || echo "[]")
SOURCE_COUNT=$(echo "$SOURCES_JSON" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$SOURCE_COUNT" -eq 0 ]; then
  echo -e "${RED}✗ No enabled sources found in Supabase. Run sql/003_seed_sources.sql first.${NC}"
  # Mark run as failed
  supa PATCH "/rest/v1/crawl_runs?id=eq.$RUN_ID" "{\"status\":\"failed\",\"notes\":\"No enabled sources\"}" > /dev/null 2>&1
  exit 1
fi

echo -e "${GREEN}✓${NC} Found $SOURCE_COUNT enabled sources"
echo "$SOURCES_JSON" | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    print(f'  • {s[\"name\"]} ({s[\"domain\"]})')
"

# Update source count
supa PATCH "/rest/v1/crawl_runs?id=eq.$RUN_ID" "{\"source_count\":$SOURCE_COUNT}" > /dev/null 2>&1

# ── Step 3: Scrape each source with Firecrawl ──
echo -e "\n${CYAN}[3/6] Scraping sources via Firecrawl...${NC}"

SCRAPED_DIR="$REPO_ROOT/.pipeline/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SCRAPED_DIR"

# Read sources into a temp file for iteration
echo "$SOURCES_JSON" | python3 -c "
import json, sys
for s in json.load(sys.stdin):
    print(json.dumps(s))
" > "$SCRAPED_DIR/sources.jsonl"

while IFS= read -r line; do
  SRC_ID=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['id'])" 2>/dev/null)
  SRC_NAME=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['name'])" 2>/dev/null)
  SRC_URL=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['url'])" 2>/dev/null)
  EXTRACTION_MODE=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('extraction_mode','homepage_links'))" 2>/dev/null)
  SOURCE_LIMIT=$(articles_limit_for_source "$SRC_NAME")
  
  echo -e "\n  ${YELLOW}→${NC} Discovering articles for ${BOLD}$SRC_NAME${NC} ($SRC_URL) [limit=$SOURCE_LIMIT]..."

  set +e
  DISCOVERY_JSON=$(SUPABASE_URL="$SUPABASE_URL" SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_KEY" FIRECRAWL_KEY="$FIRECRAWL_KEY" \
    python3 "$SCRIPT_DIR/_discover_article_urls.py" "$SRC_NAME" "$SRC_URL" "$EXTRACTION_MODE" "$SOURCE_LIMIT")
  DISCOVERY_EXIT=$?
  set -e

  if [ "$DISCOVERY_EXIT" -ne 0 ] || [ -z "$DISCOVERY_JSON" ]; then
    echo -e "    ${RED}✗${NC} Failed to discover article URLs for $SRC_NAME: $DISCOVERY_JSON"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  DISCOVERED_COUNT=$(echo "$DISCOVERY_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('candidate_count',0))" 2>/dev/null || echo "0")
  echo -e "    ${GREEN}✓${NC} Discovered $DISCOVERED_COUNT candidate articles"

  if [ "$DISCOVERED_COUNT" -eq 0 ]; then
    continue
  fi

  ANALYSIS_JSONL="$SCRAPED_DIR/${SRC_NAME// /_}_analysis.jsonl"
  : > "$ANALYSIS_JSONL"
  SOURCE_INSERTED=0
  SOURCE_DUPES=0
  SOURCE_ENTITYS=0
  SOURCE_ANALYSIS_ERRORS=0

  while IFS=$'\t' read -r ARTICLE_URL TITLE_HINT SCORE_HINT; do
    echo -e "    ${YELLOW}→${NC} Scraping article: ${ARTICLE_URL}"

    ARTICLE_TMP=$(mktemp "$SCRAPED_DIR/.article_md_XXXXXX")
    set +e
    SCRAPE_JSON=$(FIRECRAWL_KEY="$FIRECRAWL_KEY" python3 "$SCRIPT_DIR/_scrape_markdown.py" "$ARTICLE_URL")
    SCRAPE_EXIT=$?
    set -e

    echo "$SCRAPE_JSON" | python3 -c 'import sys, json; d=json.load(sys.stdin); print(d.get("markdown", ""), end="")' > "$ARTICLE_TMP" 2>/dev/null || true

    if [ "$SCRAPE_EXIT" -ne 0 ] || [ ! -s "$ARTICLE_TMP" ]; then
      echo -e "    ${RED}✗${NC} Failed to scrape article content for $SRC_NAME: $SCRAPE_JSON"
      rm -f "$ARTICLE_TMP"
      ERRORS=$((ERRORS + 1))
      SOURCE_ANALYSIS_ERRORS=$((SOURCE_ANALYSIS_ERRORS + 1))
      continue
    fi

    WORD_COUNT=$(wc -w < "$ARTICLE_TMP" | tr -d ' ')
    SAFE_TITLE=$(printf '%s' "$TITLE_HINT" | tr '/:' '__' | tr -cd '[:alnum:]_ .-')
    if [ -n "$SAFE_TITLE" ]; then
      cp "$ARTICLE_TMP" "$SCRAPED_DIR/${SRC_NAME// /_}__${SAFE_TITLE:0:80}.md" 2>/dev/null || true
    fi

    if [ "$WORD_COUNT" -lt "$MIN_WORDS_FOR_LLM" ]; then
      echo -e "    ${YELLOW}⚠${NC} Only $WORD_COUNT words (< $MIN_WORDS_FOR_LLM threshold). Skipping article analysis."
      rm -f "$ARTICLE_TMP"
      continue
    fi

    echo -e "    ${YELLOW}→${NC} Analyzing article with Qwen 3.6 (timeout=${LLM_TIMEOUT}s)..."
    set +e
    ANALYSIS_OUT=$(SRC_NAME="$SRC_NAME" SRC_URL="$SRC_URL" ARTICLE_URL="$ARTICLE_URL" TITLE_HINT="$TITLE_HINT" HERMES_URL="$HERMES_URL" HERMES_KEY="$HERMES_KEY" MODEL="$MODEL" LLM_MAX_TOKENS="$LLM_MAX_TOKENS" LLM_TIMEOUT="$LLM_TIMEOUT" python3 "$SCRIPT_DIR/_analyze_article.py" "$ARTICLE_TMP")
    ANALYSIS_EXIT=$?
    set -e
    rm -f "$ARTICLE_TMP"

    if [ "$ANALYSIS_EXIT" -ne 0 ] || [ -z "$ANALYSIS_OUT" ]; then
      echo -e "    ${RED}✗${NC} Article analysis failed for $SRC_NAME: $ANALYSIS_OUT"
      ERRORS=$((ERRORS + 1))
      SOURCE_ANALYSIS_ERRORS=$((SOURCE_ANALYSIS_ERRORS + 1))
      continue
    fi

    printf '%s\n' "$ANALYSIS_OUT" >> "$ANALYSIS_JSONL"
  done < <(
    echo "$DISCOVERY_JSON" | python3 -c 'import sys, json
d = json.load(sys.stdin)
for item in d.get("candidates", []):
    url = item.get("url", "")
    title = (item.get("title") or "").replace("\t", " ").replace("\n", " ")
    score = item.get("score", 0)
    print("{}\t{}\t{}".format(url, title, score))'
  )

  ARTICLE_COUNT=$(wc -l < "$ANALYSIS_JSONL" | tr -d ' ')
  echo -e "    ${GREEN}✓${NC} Extracted $ARTICLE_COUNT analyzed articles"

  if [ "$ARTICLE_COUNT" -gt 0 ]; then
    echo -e "    ${YELLOW}→${NC} Writing to Supabase..."
    set +e
    WRITE_RESULT=$(SRC_ID="$SRC_ID" RUN_ID="$RUN_ID" SUPABASE_URL="$SUPABASE_URL" SUPABASE_KEY="$SUPABASE_KEY" python3 "$SCRIPT_DIR/_write_pipeline_output.py" "$ANALYSIS_JSONL" "$SRC_NAME" 2>&1)
    WRITE_EXIT=$?
    set -e

    if [ "$WRITE_EXIT" -eq 0 ]; then
      INSERTED=$(echo "$WRITE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('articles_inserted',0))" 2>/dev/null || echo "0")
      DUPES=$(echo "$WRITE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('articles_duplicate',0))" 2>/dev/null || echo "0")
      ART_ERRS=$(echo "$WRITE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('articles_errors',0))" 2>/dev/null || echo "0")
      ENT_OK=$(echo "$WRITE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('entity_links_success',0))" 2>/dev/null || echo "0")
      ENT_ERRS=$(echo "$WRITE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('entity_links_errors',0))" 2>/dev/null || echo "0")

      TOTAL_ARTICLES=$((TOTAL_ARTICLES + INSERTED + DUPES))
      ERRORS=$((ERRORS + ART_ERRS + ENT_ERRS))
      SOURCE_INSERTED=$INSERTED
      SOURCE_DUPES=$DUPES
      SOURCE_ENTITYS=$ENT_OK

      if [ "$DUPES" -gt 0 ]; then
        echo -e "    ${GREEN}✓${NC} Written: ${INSERTED} new, ${DUPES} duplicates (skipped), ${ENT_OK} entities linked"
      else
        echo -e "    ${GREEN}✓${NC} Written: ${INSERTED} articles, ${ENT_OK} entities linked"
      fi
      if [ "$ART_ERRS" -gt 0 ] || [ "$ENT_ERRS" -gt 0 ]; then
        echo -e "    ${YELLOW}⚠${NC} ${ART_ERRS} article errors, ${ENT_ERRS} entity link errors"
      fi
    else
      echo -e "    ${RED}✗${NC} Write helper failed (exit=$WRITE_EXIT): $WRITE_RESULT"
      ERRORS=$((ERRORS + ARTICLE_COUNT))
    fi
  else
    echo -e "    ${YELLOW}⚠${NC} No new analyzed articles found for $SRC_NAME"
  fi
done < "$SCRAPED_DIR/sources.jsonl"

# ── Step 6: Update crawl run & generate digest ──
echo -e "\n${CYAN}[6/6] Finalizing...${NC}"

RUN_END=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FINAL_STATUS="success"
if [ "$ERRORS" -gt 0 ]; then
  FINAL_STATUS="partial_success"
fi

supa PATCH "/rest/v1/crawl_runs?id=eq.$RUN_ID" "{
  \"completed_at\": \"$RUN_END\",
  \"status\": \"$FINAL_STATUS\",
  \"article_count\": $TOTAL_ARTICLES,
  \"error_count\": $ERRORS,
  \"notes\": \"Manual pipeline run. Scraped $SOURCE_COUNT sources. See $SCRAPED_DIR for raw data.\"
}" > /dev/null 2>&1

# ── Generate Terminal Digest ──
echo -e "\n${BOLD}${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║              INTELLIGENCE DIGEST                       ║${NC}"
echo -e "${BOLD}${CYAN}╠══════════════════════════════════════════════════════╣${NC}"

# Fetch articles from this run
DIGEST_JSON=$(supa GET "/rest/v1/articles?crawl_run_id=eq.$RUN_ID&select=title,summary,priority_level,topic_tags,url" 2>/dev/null || echo "[]")

echo "$DIGEST_JSON" | python3 -c "
import json, sys
articles = json.load(sys.stdin)
print(f'  Run ID:     \033[0;36m$RUN_ID\033[0m')
print(f'  Sources:    $SOURCE_COUNT')
print(f'  Articles:   {len(articles)}')
print(f'  Errors:     $ERRORS')
print(f'  Raw data:   $SCRAPED_DIR')
print()
for i, a in enumerate(articles):
    tags = json.loads(a.get('topic_tags', '[]')) if isinstance(a.get('topic_tags'), str) else a.get('topic_tags', [])
    p = a.get('priority_level', 'medium')
    icon = '🔴' if p == 'high' else '🟡' if p == 'medium' else '🟢'
    print(f'  {icon} [{p.upper()}] {a[\"title\"][:100]}')
    if a.get('summary'):
        print(f'     {a[\"summary\"][:150]}...')
    print()
" 2>/dev/null

echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════╝${NC}"

DIGEST_PREVIEW="BioMyne Koji Digest | Run ${RUN_ID} | Sources ${SOURCE_COUNT} | Articles ${TOTAL_ARTICLES} | Errors ${ERRORS}"
supa POST /rest/v1/delivery_logs "{
  \"crawl_run_id\": \"$RUN_ID\",
  \"channel_type\": \"manual_terminal\",
  \"destination\": \"stdout\",
  \"delivered_at\": \"$RUN_END\",
  \"status\": \"generated_local_only\",
  \"message_preview\": \"$DIGEST_PREVIEW\"
}" > /dev/null 2>&1 || true

# ── Optional: Save digest markdown ──
cat > "$SCRAPED_DIR/digest.md" << DIGESTEOF
# BioMyne Koji — Intelligence Digest
**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Run ID:** $RUN_ID
**Sources:** $SOURCE_COUNT | **Articles:** $TOTAL_ARTICLES | **Errors:** $ERRORS

---
DIGESTEOF

echo "$DIGEST_JSON" | python3 -c "
import json, sys
articles = json.load(sys.stdin)
for a in articles:
    tags = json.loads(a.get('topic_tags', '[]')) if isinstance(a.get('topic_tags'), str) else a.get('topic_tags', [])
    print(f\"### {a.get('title', 'Untitled')}\")
    print(f\"**Priority:** {a.get('priority_level', 'N/A')} | **Tags:** {', '.join(tags) if tags else 'N/A'}\")
    print(f\"**URL:** {a.get('url', 'N/A')}\")
    print()
    print(a.get('summary', 'No summary available.'))
    print()
    print('---')
    print()
" >> "$SCRAPED_DIR/digest.md" 2>/dev/null

LANGFUSE_TRACE_RESULT=$(printf '%s' "{
  \"run_id\": \"$RUN_ID\",
  \"trigger\": \"manual\",
  \"model\": \"$MODEL\",
  \"status\": \"$FINAL_STATUS\",
  \"source_count\": $SOURCE_COUNT,
  \"article_count\": $TOTAL_ARTICLES,
  \"error_count\": $ERRORS,
  \"delivery_channel\": \"$DELIVERY_CHANNEL\",
  \"scraped_dir\": \"$SCRAPED_DIR\"
}" | python3 "$SCRIPT_DIR/_emit_langfuse_run_trace.py" 2>/dev/null || echo '{"status":"error"}')

FINALIZED=1

echo -e "\n${GREEN}${BOLD}✓ Pipeline complete!${NC}"
echo -e "${CYAN}  Digest saved: $SCRAPED_DIR/digest.md${NC}"
echo -e "${CYAN}  Raw data:     $SCRAPED_DIR/${NC}"
echo -e "${CYAN}  Supabase:     $SUPABASE_URL${NC}"
echo -e "${CYAN}  Langfuse:     http://localhost:3001${NC}"
echo -e "${CYAN}  Langfuse trace: $(echo "$LANGFUSE_TRACE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('trace_url', d.get('status', 'unknown')))" 2>/dev/null)${NC}"
