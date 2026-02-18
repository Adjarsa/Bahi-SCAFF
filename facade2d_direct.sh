#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_SCRIPT="${ROOT_DIR}/scripts/install_facade2d.sh"
PROCESS_SCRIPT="${ROOT_DIR}/scripts/facade2d_process.sh"
API_SCRIPT="${ROOT_DIR}/scripts/facade2d_api.sh"

usage() {
  cat <<'EOF'
Facade2D - Fichier direct d'installation/exécution

Usage:
  bash facade2d_direct.sh install
  bash facade2d_direct.sh process --input ./photo.jpg --output ./out [--corners "..."] [--reference "..."]
  bash facade2d_direct.sh api

Raccourci:
  bash facade2d_direct.sh --input ./photo.jpg --output ./out
  (équivaut à "process")
EOF
}

ensure_installed() {
  if python3 -c "import facade2d" >/dev/null 2>&1; then
    return 0
  fi

  echo "[facade2d] Installation automatique..."
  bash "${INSTALL_SCRIPT}"

  if ! python3 -c "import facade2d" >/dev/null 2>&1; then
    echo "[facade2d] Erreur: installation incomplète."
    exit 1
  fi
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

MODE="$1"

case "${MODE}" in
  install)
    exec bash "${INSTALL_SCRIPT}"
    ;;
  api)
    ensure_installed
    shift
    exec bash "${API_SCRIPT}" "$@"
    ;;
  process)
    ensure_installed
    shift
    exec bash "${PROCESS_SCRIPT}" "$@"
    ;;
  -h|--help|help)
    usage
    exit 0
    ;;
  *)
    # Mode implicite: process
    ensure_installed
    exec bash "${PROCESS_SCRIPT}" "$@"
    ;;
esac
