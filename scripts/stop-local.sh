#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"

kill_from_pid_file() {
  local pid_file="$1"
  local label="$2"
  if [[ ! -f "$pid_file" ]]; then
    echo "$label: aucun PID trouve."
    return
  fi

  local pid
  pid="$(cat "$pid_file" || true)"
  if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
    echo "$label arrete (PID $pid)."
  else
    echo "$label: processus deja arrete."
  fi
  rm -f "$pid_file"
}

kill_from_pid_file "$RUN_DIR/backend.pid" "Backend"
kill_from_pid_file "$RUN_DIR/frontend.pid" "Frontend"
