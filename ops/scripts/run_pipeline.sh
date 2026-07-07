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
MAX_ARTICLES_PER_SOURCE="${MAX_ARTICLES_PER_SOURCE:-3}"
DELIVERY_CHANNEL="${DELIVERY_CHANNEL:-manual_terminal}"

# ── Colors ──
BOLD='\033[1m'; CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

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
SOURCES_JSON=$(supa GET "/rest/v1/sources?select=id,name,url,domain&enabled=eq.true")
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

TOTAL_ARTICLES=0
ERRORS=0
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
  
  echo -e "\n  ${YELLOW}→${NC} Scraping ${BOLD}$SRC_NAME${NC} ($SRC_URL)..."
  
  SCRAPE_RESP=$(curl -s --max-time 30 -X POST https://api.firecrawl.dev/v1/scrape \
    -H "Authorization: Bearer $FIRECRAWL_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$SRC_URL\", \"formats\": [\"markdown\"], \"onlyMainContent\": true}" 2>/dev/null)
  
  if echo "$SCRAPE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('success') else 1)" 2>/dev/null; then
    MARKDOWN=$(echo "$SCRAPE_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'].get('markdown',''))" 2>/dev/null)
    WORD_COUNT=$(echo "$MARKDOWN" | wc -w | tr -d ' ')
    
    # Save raw scraped content
    echo "$MARKDOWN" > "$SCRAPED_DIR/${SRC_NAME// /_}.md"
    echo -e "    ${GREEN}✓${NC} Scraped $WORD_COUNT words → $SCRAPED_DIR/${SRC_NAME// /_}.md"
    
    # ── Step 4: LLM Analysis ──
    echo -e "    ${YELLOW}→${NC} Analyzing with Qwen 3.6..."
    
    # Truncate markdown to avoid overwhelming the model
    MARKDOWN_TRUNC=$(echo "$MARKDOWN" | head -c 8000)
    
    ANALYSIS_PROMPT="You are a biotech intelligence analyst. Analyze the following scraped content from ${SRC_NAME} (${SRC_URL}).

Extract the top ${MAX_ARTICLES_PER_SOURCE} biotech/pharma news items or articles from this content. For each item, output a JSON object with this EXACT structure (output ONLY the JSON array, no other text):

[
  {
    \"title\": \"Article headline\",
    \"url\": \"Article URL if available, otherwise source URL\",
    \"summary\": \"2-3 sentence summary of key findings\",
    \"topic_tags\": [\"tag1\", \"tag2\"],
    \"priority_level\": \"high|medium|low\",
    \"entities\": [
      {\"name\": \"Company or drug name\", \"entity_type\": \"company|drug|person|technology|deal\"}
    ]
  }
]

SCRAPED CONTENT:
${MARKDOWN_TRUNC}"

    REQUEST_JSON=$(printf '%s' "$ANALYSIS_PROMPT" | python3 "$SCRIPT_DIR/_build_llm_request.py")
    ANALYSIS_JSON=$(curl -s --max-time 180 \
      -H "Authorization: Bearer $HERMES_KEY" \
      -H "Content-Type: application/json" \
      "$HERMES_URL/v1/chat/completions" \
      -d "$REQUEST_JSON" 2>/dev/null)
    
    # Extract the JSON array from LLM response
    ARTICLES_JSON=$(echo "$ANALYSIS_JSON" | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
    content = d['choices'][0]['message']['content']
    # Try to find JSON array in the response
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        parsed = json.loads(match.group())
        print(json.dumps(parsed))
    else:
        print('[]')
except Exception as e:
    print('[]', file=sys.stderr)
    sys.exit(0)
" 2>/dev/null || echo "[]")
    
    ARTICLE_COUNT=$(echo "$ARTICLES_JSON" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo -e "    ${GREEN}✓${NC} Extracted $ARTICLE_COUNT articles"
    
    # ── Step 5: Write to Supabase ──
    if [ "$ARTICLE_COUNT" -gt 0 ]; then
      echo -e "    ${YELLOW}→${NC} Writing to Supabase..."
      
      printf '%s' "$ARTICLES_JSON" | SRC_ID="$SRC_ID" RUN_ID="$RUN_ID" python3 -c "
import json, sys, uuid, os

articles = json.load(sys.stdin)
src_id = os.environ.get('SRC_ID', '')
run_id = os.environ.get('RUN_ID', '')
supa_url = os.environ.get('SUPABASE_URL', '')
supa_key = os.environ.get('SUPABASE_KEY', '')

for a in articles:
    article_id = str(uuid.uuid4())
    print(json.dumps({
        'id': article_id,
        'source_id': src_id,
        'crawl_run_id': run_id,
        'title': a.get('title', 'Untitled'),
        'url': a.get('url', ''),
        'summary': a.get('summary', ''),
        'topic_tags': json.dumps(a.get('topic_tags', [])),
        'priority_level': a.get('priority_level', 'medium'),
        'status': 'analyzed'
    }))
    
    # Output entities separately
    for e in a.get('entities', []):
        entity_id = str(uuid.uuid4())
        print('ENTITY:' + json.dumps({
            'article_id': article_id,
            'entity_id': entity_id,
            'name': e.get('name', ''),
            'entity_type': e.get('entity_type', 'company'),
            'role_in_article': 'mentioned',
            'mention_count': 1
        }))
" 2>/dev/null > "$SCRAPED_DIR/${SRC_NAME// /_}_articles.jsonl" || true
      
      # Process saved articles and insert into Supabase
      while IFS= read -r aline; do
        if [[ "$aline" == ENTITY:* ]]; then
          ENTITY_DATA="${aline#ENTITY:}"
          # Insert entity
          ENTITY_NAME=$(echo "$ENTITY_DATA" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['name'])" 2>/dev/null)
          ENTITY_TYPE=$(echo "$ENTITY_DATA" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['entity_type'])" 2>/dev/null)
          ARTICLE_ID=$(echo "$ENTITY_DATA" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['article_id'])" 2>/dev/null)
          
          # Upsert entity
          ENTITY_RESP=$(curl -s --max-time 15 -X POST "${SUPABASE_URL}/rest/v1/entities?on_conflict=name,entity_type" \
            -H "apikey: ${SUPABASE_KEY}" \
            -H "Authorization: Bearer ${SUPABASE_KEY}" \
            -H "Content-Type: application/json" \
            -H "Prefer: resolution=merge-duplicates,return=representation" \
            -d "{
            \"name\": \"$ENTITY_NAME\",
            \"entity_type\": \"$ENTITY_TYPE\"
          }" 2>/dev/null)
          
          # Get entity ID (from insert or existing)
          ENT_DB_ID=$(echo "$ENTITY_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if isinstance(d,list) and len(d)>0 else '')" 2>/dev/null || echo "")
          
          if [ -n "$ENT_DB_ID" ] && [ -n "$ARTICLE_ID" ]; then
            ARTICLE_ENTITY_RESP=$(supa POST /rest/v1/article_entities "{
              \"article_id\": \"$ARTICLE_ID\",
              \"entity_id\": \"$ENT_DB_ID\",
              \"role_in_article\": \"mentioned\",
              \"mention_count\": 1
            }" 2>/dev/null)

            if ! echo "$ARTICLE_ENTITY_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if isinstance(d,list) and len(d) > 0 else 1)" 2>/dev/null; then
              echo -e "    ${RED}✗${NC} Failed to link article entity for $SRC_NAME" >&2
              ERRORS=$((ERRORS + 1))
            fi
          fi
        else
          # Insert article
          ARTICLE_DATA="$aline"
          ARTICLE_RESP=$(supa POST /rest/v1/articles "$ARTICLE_DATA" 2>/dev/null)

          if echo "$ARTICLE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if isinstance(d,list) and len(d) > 0 else 1)" 2>/dev/null; then
            TOTAL_ARTICLES=$((TOTAL_ARTICLES + 1))
          else
            echo -e "    ${RED}✗${NC} Failed to insert article for $SRC_NAME" >&2
            ERRORS=$((ERRORS + 1))
          fi
        fi
      done < "$SCRAPED_DIR/${SRC_NAME// /_}_articles.jsonl"
      
      echo -e "    ${GREEN}✓${NC} Written to Supabase"
    fi
  else
    echo -e "    ${RED}✗${NC} Firecrawl scrape failed for $SRC_NAME"
    ERRORS=$((ERRORS + 1))
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
DIGEST_JSON=$(supa GET "/rest/v1/articles?crawl_run_id=eq.$RUN_ID&select=title,summary,priority_level,topic_tags,url" 2>/dev/null)

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

echo -e "\n${GREEN}${BOLD}✓ Pipeline complete!${NC}"
echo -e "${CYAN}  Digest saved: $SCRAPED_DIR/digest.md${NC}"
echo -e "${CYAN}  Raw data:     $SCRAPED_DIR/${NC}"
echo -e "${CYAN}  Supabase:     $SUPABASE_URL${NC}"
echo -e "${CYAN}  Langfuse:     http://localhost:3001${NC}"
echo -e "${CYAN}  Langfuse trace: $(echo "$LANGFUSE_TRACE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('trace_url', d.get('status', 'unknown')))" 2>/dev/null)${NC}"
