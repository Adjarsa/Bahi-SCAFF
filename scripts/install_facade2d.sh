#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-facade2d"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[facade2d] Erreur: python3 est requis."
  exit 1
fi

echo "[facade2d] Racine projet: ${ROOT_DIR}"
echo "[facade2d] Environnement virtuel: ${VENV_DIR}"

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -e "${ROOT_DIR}"

cat <<'EOF'

Installation terminée.

Utilisation CLI:
  source .venv-facade2d/bin/activate
  facade2d process --input ./photo.jpg --output ./out

Utilisation API:
  source .venv-facade2d/bin/activate
  facade2d-api

EOF
