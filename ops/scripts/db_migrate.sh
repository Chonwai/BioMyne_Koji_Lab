#!/bin/bash
# DB migration helper for BioMyne Koji
#
# Usage:
#   ./ops/scripts/db_migrate.sh dry-run    # show pending migrations (no apply)
#   ./ops/scripts/db_migrate.sh push       # apply pending migrations
#   ./ops/scripts/db_migrate.sh list       # show local vs remote status
#   ./ops/scripts/db_migrate.sh new <name> # create a new timestamped migration file
#   ./ops/scripts/db_migrate.sh status     # check which migrations are applied
#
# Prerequisites:
#   - supabase CLI installed (brew install supabase/tap/supabase)
#   - SUPABASE_PROJECT_REF set in .env or environment
#   - SUPABASE_DB_PASSWORD set in .env or environment (postgres password from Dashboard → Settings → Database)
#
# Golden rules:
#   - NEVER edit a migration after it has been applied (use forward-fix migrations)
#   - NEVER edit schema directly in Supabase SQL Editor (causes sync errors on next db push)
#   - ALWAYS dry-run before push

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# --- Early help (no credentials required) ---
if [ $# -eq 0 ] || [ "${1:-}" = "help" ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'EOF'
DB Migration Helper for BioMyne Koji

Usage:
  ./ops/scripts/db_migrate.sh dry-run    Show pending migrations (no apply)
  ./ops/scripts/db_migrate.sh push       Apply pending migrations (with confirmation)
  ./ops/scripts/db_migrate.sh list       Show local vs remote status
  ./ops/scripts/db_migrate.sh new <name> Create a new timestamped migration file
  ./ops/scripts/db_migrate.sh status     Check applied migrations on remote

Environment (from .env or shell export):
  SUPABASE_PROJECT_REF   Your Supabase project ref (e.g. yihgpsbofjgoxbfypnia)
  SUPABASE_DB_PASSWORD   Postgres password (Dashboard → Settings → Database)

Golden Rules:
  1. NEVER edit a migration after it has been applied
  2. NEVER edit schema directly in Supabase SQL Editor
  3. ALWAYS dry-run before push
EOF
  exit 0
fi

# --- Load .env if present ---
if [ -f "$REPO_ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.env"
  set +a
fi

# --- Resolve project ref ---
SUPABASE_PROJECT_REF="${SUPABASE_PROJECT_REF:-}"
if [ -z "$SUPABASE_PROJECT_REF" ]; then
  echo "ERROR: SUPABASE_PROJECT_REF is not set."
  echo "  Set it in .env or export it in your shell."
  echo "  Example: SUPABASE_PROJECT_REF=yihgpsbofjgoxbfypnia"
  exit 1
fi

# --- Resolve DB password ---
SUPABASE_DB_PASSWORD="${SUPABASE_DB_PASSWORD:-}"
if [ -z "$SUPABASE_DB_PASSWORD" ]; then
  echo "ERROR: SUPABASE_DB_PASSWORD is not set."
  echo "  Get it from: Supabase Dashboard → Settings → Database → Connection string → Password"
  echo "  Then set it in .env: SUPABASE_DB_PASSWORD=<your-password>"
  exit 1
fi

DB_URL="postgresql://postgres.${SUPABASE_PROJECT_REF}:${SUPABASE_DB_PASSWORD}@db.${SUPABASE_PROJECT_REF}.supabase.co:5432/postgres"

# --- Commands ---
case "${1:-help}" in
  dry-run)
    echo "=== Dry Run: migrations that would be applied ==="
    echo "Project: $SUPABASE_PROJECT_REF"
    echo ""
    supabase db push --db-url "$DB_URL" --dry-run
    ;;
  push)
    echo "=== Applying pending migrations ==="
    echo "Project: $SUPABASE_PROJECT_REF"
    echo ""
    echo "⚠ This will modify the remote database. Ctrl+C to abort."
    echo ""
    read -r -p "Type 'yes' to confirm: " confirm
    if [ "$confirm" != "yes" ]; then
      echo "Aborted."
      exit 0
    fi
    supabase db push --db-url "$DB_URL"
    echo ""
    echo "✅ Migrations applied. Run './ops/scripts/db_migrate.sh list' to verify."
    ;;
  list)
    echo "=== Migration Status ==="
    echo "Project: $SUPABASE_PROJECT_REF"
    echo ""
    supabase migration list
    ;;
  new)
    name="${2:?Usage: db_migrate.sh new <name>}"
    supabase migration new "$name"
    echo ""
    echo "✅ Created. Write your SQL in supabase/migrations/*.sql, then dry-run."
    ;;
  status)
    echo "=== Applied Migrations (remote) ==="
    echo "Project: $SUPABASE_PROJECT_REF"
    echo ""
    supabase migration list --db-url "$DB_URL"
    ;;
  help|*)
    cat <<'EOF'
DB Migration Helper for BioMyne Koji

Usage:
  ./ops/scripts/db_migrate.sh dry-run    Show pending migrations (no apply)
  ./ops/scripts/db_migrate.sh push       Apply pending migrations (with confirmation)
  ./ops/scripts/db_migrate.sh list       Show local vs remote status
  ./ops/scripts/db_migrate.sh new <name> Create a new timestamped migration file
  ./ops/scripts/db_migrate.sh status     Check applied migrations on remote

Environment (from .env or shell export):
  SUPABASE_PROJECT_REF   Your Supabase project ref (e.g. yihgpsbofjgoxbfypnia)
  SUPABASE_DB_PASSWORD   Postgres password (Dashboard → Settings → Database)

Golden Rules:
  1. NEVER edit a migration after it has been applied
  2. NEVER edit schema directly in Supabase SQL Editor
  3. ALWAYS dry-run before push
EOF
    exit 0
    ;;
esac
