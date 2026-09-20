#!/usr/bin/env bash
# ============================================================
# BioMyne Koji — Local Demo Environment Launcher
# ============================================================
# Usage:
#   ./scripts/demo_start.sh            # 啟動完整 demo 環境
#   ./scripts/demo_start.sh dashboard  # 只啟動 dashboard（前端）
#   ./scripts/demo_start.sh pipeline   # 只啟動 pipeline（後端手動跑一次）
#   ./scripts/demo_start.sh langfuse   # 只啟動 Langfuse（observability）
#   ./scripts/demo_start.sh status     # 檢查所有服務狀態
#   ./scripts/demo_start.sh stop       # 停止 dashboard + langfuse
#
# Demo 前請確保：
#   1. Supabase project 可達（REST + DB 憑證在 .env）
#   2. Ollama 已安裝 qwen3.6:35b-mlx（ollama list）
#   3. 前端 node_modules 已安裝（npm install）
# ============================================================

set -euo pipefail

# ─── Paths ───
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KOJI_DIR="$ROOT"
DASHBOARD_DIR="$ROOT/../biomyne-koji-dashboard"
VENV_PY="$KOJI_DIR/.venv/bin/python3"
DASHBOARD_PORT=3300

# ─── Colors ───
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

log()  { echo -e "${CYAN}[demo]${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*"; }

# ─── Pre-flight checks ───
preflight() {
  log "Pre-flight checks..."
  [ -d "$KOJI_DIR/.venv" ] && ok "Backend venv: $KOJI_DIR/.venv" || warn "Backend venv missing (run: cd $KOJI_DIR && python3.12 -m venv .venv)"
  [ -d "$DASHBOARD_DIR/node_modules" ] && ok "Dashboard node_modules" || warn "Dashboard deps missing (run: cd $DASHBOARD_DIR && npm install)"
  if [ -f "$KOJI_DIR/.env" ]; then
    grep -q 'SUPABASE_URL' "$KOJI_DIR/.env" && ok "Backend .env SUPABASE_URL" || fail "Backend .env missing SUPABASE_URL"
    grep -q 'SUPABASE_DB_PASSWORD' "$KOJI_DIR/.env" && ok "Backend .env DB password" || warn "Backend .env missing SUPABASE_DB_PASSWORD"
  else
    fail "Backend .env missing (copy .env.example → .env and fill)"
  fi
  local ollama_models
  ollama_models="$(curl -s -m 5 http://localhost:11434/api/tags 2>/dev/null || echo '{}')"
  if echo "$ollama_models" | python3 -c "import sys,json;models=json.load(sys.stdin).get('models',[]);print(any('qwen' in m.get('name','').lower() for m in models))" 2>/dev/null | grep -q True; then
    ok "Ollama + qwen3.6 model ready"
  elif echo "$ollama_models" | python3 -c "import sys,json;models=json.load(sys.stdin).get('models',[]);print(len(models))" 2>/dev/null | grep -q '[1-9]'; then
    warn "Ollama running but qwen3.6 not found (run: ollama pull qwen3.6:35b-mlx)"
  else
    warn "Ollama not running (run: ollama serve)"
  fi
}

# ─── Hermes Gateway (Docker :8642 — LLM pipeline backend) ───
start_hermes() {
  log "Starting Hermes Gateway (Docker :8642)..."
  cd "$KOJI_DIR"
  if docker ps 2>/dev/null | grep -q koji-hermes; then
    ok "Hermes Gateway already running"
  else
    docker compose up -d hermes-agent 2>&1 | tail -2
    log "Waiting for Hermes Gateway to be ready..."
    for i in $(seq 1 20); do
      sleep 2
      if curl -s -m 3 "$HERMES_URL/health" 2>/dev/null | python3 -c "import sys,json;sys.exit(0 if json.load(sys.stdin).get('status')=='ok' else 1)" 2>/dev/null; then
        ok "Hermes Gateway ready at $HERMES_URL"
        return 0
      fi
    done
    warn "Hermes Gateway may still be starting — check docker compose logs hermes-agent"
  fi
}

# ─── Dashboard (Next.js :3300) ───
start_dashboard() {
  log "Starting Dashboard (Next.js on :$DASHBOARD_PORT)..."
  cd "$DASHBOARD_DIR"
  if lsof -i :"$DASHBOARD_PORT" >/dev/null 2>&1; then
    ok "Dashboard already running on :$DASHBOARD_PORT"
  else
    nohup npm run dev > /tmp/koji-dashboard.log 2>&1 &
    sleep 4
    if lsof -i :"$DASHBOARD_PORT" >/dev/null 2>&1; then
      ok "Dashboard up on http://localhost:$DASHBOARD_PORT"
    else
      warn "Dashboard starting... check /tmp/koji-dashboard.log"
    fi
  fi
}

# ─── Pipeline (backend manual run) ───
run_pipeline() {
  log "Running Koji pipeline (single pass, sources from Supabase)..."
  cd "$KOJI_DIR"
  set -a; source .env; set +a
  export CRAWLER_PROVIDER="${CRAWLER_PROVIDER:-local}"
  export CRAWLER_ALLOW_CLOUD="${CRAWLER_ALLOW_CLOUD:-true}"
  ok "Provider routing: local (8 easy) + firecrawl_cloud (3 hard)"
  bash ops/scripts/run_pipeline.sh
}

# ─── Langfuse (Docker, observability) ───
start_langfuse() {
  log "Starting Langfuse (Docker)..."
  cd "$KOJI_DIR"
  if docker ps 2>/dev/null | grep -qi langfuse; then
    ok "Langfuse already running"
  else
    docker compose up -d langfuse 2>/dev/null || docker compose up -d
    sleep 3
    docker ps 2>/dev/null | grep -qi langfuse && ok "Langfuse up" || warn "Langfuse start check: run 'docker compose ps'"
  fi
}

# ─── Status ───
status() {
  log "Service status:"
  # 讀 SUPABASE_PROJECT_REF（從 .env，不 export 也讀得到）
  local project_ref=""
  if [ -f "$KOJI_DIR/.env" ]; then
    project_ref="$(grep -E '^SUPABASE_PROJECT_REF=' "$KOJI_DIR/.env" | cut -d= -f2 || true)"
  fi
  docker ps 2>/dev/null | grep -q koji-hermes && ok "Hermes Gateway :8642" || warn "Hermes Gateway — down (run: ./demo_start.sh hermes)"
  docker ps 2>/dev/null | grep -qi langfuse && ok "Langfuse (Docker)" || warn "Langfuse — down"
  if [ -n "$project_ref" ]; then
    curl -s -m 3 "https://$project_ref.supabase.co/rest/v1/sources?select=id&limit=1" \
      -H "apikey: $(grep SUPABASE_SERVICE_ROLE_KEY "$KOJI_DIR/.env" | cut -d= -f2)" \
      -H "Authorization: Bearer $(grep SUPABASE_SERVICE_ROLE_KEY "$KOJI_DIR/.env" | cut -d= -f2)" >/dev/null 2>&1 \
      && ok "Supabase REST reachable" || warn "Supabase REST unreachable"
  else
    warn "Supabase project ref not found in .env"
  fi
  local ollama_models
  ollama_models="$(curl -s -m 5 http://localhost:11434/api/tags 2>/dev/null || echo '{}')"
  if echo "$ollama_models" | python3 -c "import sys,json;models=json.load(sys.stdin).get('models',[]);print(any('qwen' in m.get('name','').lower() for m in models))" 2>/dev/null | grep -q True; then
    ok "Ollama + qwen3.6 model"
  elif echo "$ollama_models" | python3 -c "import sys,json;models=json.load(sys.stdin).get('models',[]);print(len(models))" 2>/dev/null | grep -q '[1-9]'; then
    warn "Ollama running but qwen3.6 not found (run: ollama pull qwen3.6:35b-mlx)"
  else
    warn "Ollama not running (run: ollama serve)"
  fi
}

# ─── Stop ───
stop_all() {
  log "Stopping services..."
  lsof -ti :"$DASHBOARD_PORT" | xargs kill 2>/dev/null && ok "Dashboard stopped" || warn "Dashboard not running"
  cd "$KOJI_DIR" && docker compose down 2>/dev/null && ok "Docker services stopped" || warn "Docker compose not running"
}

# ─── Dispatch ───
case "${1:-full}" in
  hermes)    start_hermes ;;
  dashboard) preflight; start_dashboard ;;
  pipeline)  preflight; run_pipeline ;;
  langfuse)  start_langfuse ;;
  status)    status ;;
  stop)      stop_all ;;
  full|all)
    preflight
    start_hermes
    start_langfuse
    start_dashboard
    log "────────────────────────────"
    ok "Dashboard:  http://localhost:$DASHBOARD_PORT"
    ok "Pipeline:   ./scripts/demo_start.sh pipeline  (手動跑一次後端)"
    ok "Status:     ./scripts/demo_start.sh status"
    log "────────────────────────────"
    ;;
  *) echo "Usage: $0 [full|hermes|dashboard|pipeline|langfuse|status|stop]"; exit 1 ;;
esac
