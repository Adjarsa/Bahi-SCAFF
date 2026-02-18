#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-facade2d"
PYTHON_BIN=""

if [[ -x "${VENV_DIR}/bin/python" ]]; then
  PYTHON_BIN="${VENV_DIR}/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "[facade2d] Erreur: python3 introuvable."
  exit 1
fi

if ! "${PYTHON_BIN}" -c "import facade2d" >/dev/null 2>&1; then
  echo "[facade2d] Erreur: outil non installé."
  echo "Lance d'abord: bash scripts/install_facade2d.sh"
  exit 1
fi

exec "${PYTHON_BIN}" -m facade2d.api
