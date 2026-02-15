#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
RUN_DIR="$ROOT_DIR/.run"

BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"
BACKEND_LOG="$RUN_DIR/backend.log"
FRONTEND_LOG="$RUN_DIR/frontend.log"

mkdir -p "$RUN_DIR"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Commande manquante: $1"
    exit 1
  fi
}

is_pid_running() {
  local pid="$1"
  if [[ -z "$pid" ]]; then
    return 1
  fi
  kill -0 "$pid" >/dev/null 2>&1
}

start_backend() {
  if [[ -f "$BACKEND_PID_FILE" ]]; then
    local existing_pid
    existing_pid="$(cat "$BACKEND_PID_FILE" || true)"
    if is_pid_running "$existing_pid"; then
      echo "Backend deja actif (PID $existing_pid)."
      return
    fi
  fi

  if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
    python3 -m venv "$BACKEND_DIR/.venv"
  fi

  source "$BACKEND_DIR/.venv/bin/activate"
  python3 -m pip install -r "$BACKEND_DIR/requirements.txt" >/dev/null
  deactivate

  nohup bash -lc "cd \"$BACKEND_DIR\" && source .venv/bin/activate && python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" >"$BACKEND_LOG" 2>&1 &
  echo $! >"$BACKEND_PID_FILE"
  echo "Backend demarre (PID $(cat "$BACKEND_PID_FILE"))."
}

start_frontend() {
  if [[ -f "$FRONTEND_PID_FILE" ]]; then
    local existing_pid
    existing_pid="$(cat "$FRONTEND_PID_FILE" || true)"
    if is_pid_running "$existing_pid"; then
      echo "Frontend deja actif (PID $existing_pid)."
      return
    fi
  fi

  if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    (cd "$FRONTEND_DIR" && npm install >/dev/null)
  fi

  echo "VITE_API_URL=http://127.0.0.1:8000/api/v1" >"$FRONTEND_DIR/.env.local"

  nohup bash -lc "cd \"$FRONTEND_DIR\" && npm run dev -- --host 127.0.0.1 --port 5173" >"$FRONTEND_LOG" 2>&1 &
  echo $! >"$FRONTEND_PID_FILE"
  echo "Frontend demarre (PID $(cat "$FRONTEND_PID_FILE"))."
}

wait_for_url() {
  local url="$1"
  local label="$2"
  local max_tries=60
  local i=0
  until curl -fsS "$url" >/dev/null 2>&1; do
    i=$((i + 1))
    if [[ "$i" -ge "$max_tries" ]]; then
      echo "Timeout en attente de $label: $url"
      echo "Consultez les logs:"
      echo "  - $BACKEND_LOG"
      echo "  - $FRONTEND_LOG"
      exit 1
    fi
    sleep 0.5
  done
}

main() {
  require_cmd python3
  require_cmd npm
  require_cmd curl

  start_backend
  start_frontend

  wait_for_url "http://127.0.0.1:8000/api/v1/health" "backend"
  wait_for_url "http://127.0.0.1:5173" "frontend"

  echo ""
  echo "ScaffoldPlan AI est pret:"
  echo "  - Frontend: http://127.0.0.1:5173"
  echo "  - API docs: http://127.0.0.1:8000/docs"
  echo ""
  echo "Arret:"
  echo "  ./scripts/stop-local.sh"

  if command -v open >/dev/null 2>&1; then
    open "http://127.0.0.1:5173" >/dev/null 2>&1 || true
  fi
}

main "$@"
