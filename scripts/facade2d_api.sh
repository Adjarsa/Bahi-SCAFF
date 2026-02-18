#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-facade2d"

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  echo "[facade2d] Erreur: environnement non installé."
  echo "Lance d'abord: bash scripts/install_facade2d.sh"
  exit 1
fi

exec "${VENV_DIR}/bin/python" -m facade2d.api
