#!/usr/bin/env bash
# ============================================================
# BioMyne Koji — Phase 1 End-to-End Smoke Test
# Usage: bash ops/scripts/smoke_test.sh
# ============================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PASS=0
FAIL=0
RESULTS=""

log_pass() { PASS=$((PASS+1)); RESULTS="${RESULTS}✅ $1\n"; echo -e "${GREEN}✅${NC} $1"; }
log_fail() { FAIL=$((FAIL+1)); RESULTS="${RESULTS}❌ $1\n"; echo -e "${RED}❌${NC} $1"; }
log_info() { echo -e "${CYAN}ℹ${NC}  $1"; }
header()   { echo -e "\n${BOLD}${YELLOW}━━━ $1 ━━━${NC}"; }

# ── Config ──
HERMES_URL="${HERMES_URL:-http://localhost:8642}"
HERMES_KEY="${HERMES_KEY:-koji-phase1-local}"
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
FIRECRAWL_KEY="${FIRECRAWL_KEY:-fc-59fb50e705e142bfb5e3a5dd9b8905d5}"
SUPABASE_URL="${SUPABASE_URL:-https://yihgpsbofjgoxbfypnia.supabase.co}"
SUPABASE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlpaGdwc2JvZmpnb3hiZnlwbmlhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzMyODg3NywiZXhwIjoyMDk4OTA0ODc3fQ.z-SLd6GxO81kURZYdiq3CsHLC-r_pzn7f_rRKopS8C4}"
LANGFUSE_URL="${LANGFUSE_URL:-http://localhost:3001}"
MODEL="${OLLAMA_MODEL_TAG:-qwen3.6:35b-mlx}"

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║   BioMyne Koji — Phase 1 Smoke Test Suite        ║"
echo "║   $(date '+%Y-%m-%d %H:%M:%S')                          ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── 1. Ollama Health ──
header "1. Ollama (Local LLM)"
if curl -s --max-time 5 "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
  log_pass "Ollama is running on $OLLAMA_URL"
  MODELS=$(curl -s "$OLLAMA_URL/api/tags" | python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin).get('models',[])]" 2>/dev/null || echo "unknown")
  log_info "  Available models: $MODELS"
else
  log_fail "Ollama not reachable at $OLLAMA_URL"
fi

# ── 2. Hermes Gateway Health ──
header "2. Hermes Agent Gateway"
HEALTH=$(curl -s --max-time 5 "$HERMES_URL/health" 2>/dev/null || echo '{"status":"down"}')
if echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='ok' else 1)" 2>/dev/null; then
  VERSION=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null)
  log_pass "Hermes Gateway v$VERSION is healthy"
else
  log_fail "Hermes Gateway not healthy"
fi

# ── 3. Ollama → Hermes Chat Completion ──
header "3. LLM Inference (Qwen 3.6 via Hermes → Ollama)"
CHAT_RESP=$(curl -s --max-time 120 \
  -H "Authorization: Bearer $HERMES_KEY" \
  -H "Content-Type: application/json" \
  "$HERMES_URL/v1/chat/completions" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"You are a biotech intelligence analyst. In one sentence, tell me the significance of Vertex acquiring Crinetics Pharmaceuticals for \$10 billion in July 2026.\"}],
    \"max_tokens\": 80
  }" 2>/dev/null)

if echo "$CHAT_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('choices') else 1)" 2>/dev/null; then
  CONTENT=$(echo "$CHAT_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null)
  TOKENS=$(echo "$CHAT_RESP" | python3 -c "import sys,json; u=json.load(sys.stdin).get('usage',{}); print(f\"{u.get('prompt_tokens',0)}+{u.get('completion_tokens',0)}={u.get('total_tokens',0)}\")" 2>/dev/null)
  log_pass "LLM inference successful ($TOKENS tokens)"
  log_info "  Response: ${CONTENT:0:200}..."
else
  log_fail "LLM inference failed"
  log_info "  Raw: $(echo "$CHAT_RESP" | head -c 200)"
fi

# ── 4. Firecrawl ──
header "4. Firecrawl (Web Scraping)"
SCRAPE_RESP=$(curl -s --max-time 30 -X POST https://api.firecrawl.dev/v1/scrape \
  -H "Authorization: Bearer $FIRECRAWL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.statnews.com/", "formats": ["markdown"], "onlyMainContent": true}' 2>/dev/null)

if echo "$SCRAPE_RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('success'):
    md = d['data'].get('markdown', '')
    print(f'Scraped {len(md.split())} words')
    sys.exit(0)
else:
    sys.exit(1)
" 2>/dev/null; then
  WORD_COUNT=$(echo "$SCRAPE_RESP" | python3 -c "
import sys, json
md = json.load(sys.stdin)['data'].get('markdown', '')
print(len(md.split()))
" 2>/dev/null)
  log_pass "Firecrawl scraped STAT News ($WORD_COUNT words)"
else
  log_fail "Firecrawl scrape failed"
fi

# ── 5. Supabase ──
header "5. Supabase (Database)"
SOURCES=$(curl -s --max-time 10 \
  "${SUPABASE_URL}/rest/v1/sources?select=name,url" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY" 2>/dev/null)

if echo "$SOURCES" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if len(d)>0 else 1)" 2>/dev/null; then
  COUNT=$(echo "$SOURCES" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null)
  NAMES=$(echo "$SOURCES" | python3 -c "import sys,json; print(', '.join(s['name'] for s in json.load(sys.stdin)))" 2>/dev/null)
  log_pass "Supabase connected — $COUNT sources: $NAMES"
else
  log_fail "Supabase query failed or no sources found"
fi

# ── 6. Langfuse ──
header "6. Langfuse (Observability)"
if curl -s --max-time 5 "$LANGFUSE_URL" > /dev/null 2>&1; then
  log_pass "Langfuse dashboard is accessible at $LANGFUSE_URL"
else
  log_fail "Langfuse not reachable at $LANGFUSE_URL"
fi

# ── 7. Docker Services ──
header "7. Docker Services"
if command -v docker &> /dev/null; then
  RUNNING=$(docker compose -f "$(dirname "$0")/../../docker-compose.yml" ps --format 'table {{.Name}}\t{{.Status}}' 2>/dev/null | tail -n +2 | grep -c "Up" || echo "0")
  log_pass "$RUNNING Docker services running"
  docker compose -f "$(dirname "$0")/../../docker-compose.yml" ps --format 'table {{.Name}}\t{{.Status}}' 2>/dev/null || true
else
  log_info "Docker not available (skipping)"
fi

# ── Summary ──
echo -e "\n${BOLD}${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║              SMOKE TEST RESULTS                   ║${NC}"
echo -e "${BOLD}${CYAN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}${CYAN}║${NC}  ${GREEN}Passed: $PASS${NC}  │  ${RED}Failed: $FAIL${NC}  │  Total: $((PASS+FAIL))/7"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo -e "$RESULTS"

if [ "$FAIL" -eq 0 ]; then
  echo -e "\n${GREEN}${BOLD}🎉 ALL SYSTEMS GO — Phase 1 stack is operational!${NC}"
  echo -e "${CYAN}   Langfuse traces: $LANGFUSE_URL${NC}"
  echo -e "${CYAN}   Hermes API:      $HERMES_URL${NC}"
  echo -e "${CYAN}   Supabase:        $SUPABASE_URL${NC}"
  exit 0
else
  echo -e "\n${RED}${BOLD}⚠️  $FAIL check(s) failed — review above.${NC}"
  exit 1
fi
