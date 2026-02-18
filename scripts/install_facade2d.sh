#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-facade2d"
MODE="venv"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[facade2d] Erreur: python3 est requis."
  exit 1
fi

echo "[facade2d] Racine projet: ${ROOT_DIR}"
echo "[facade2d] Environnement virtuel: ${VENV_DIR}"

if python3 -m venv "${VENV_DIR}" >/tmp/facade2d_venv.log 2>&1; then
  "${VENV_DIR}/bin/python" -m pip install --upgrade pip
  "${VENV_DIR}/bin/python" -m pip install -e "${ROOT_DIR}"
else
  MODE="user"
  echo "[facade2d] Avertissement: impossible de créer un venv, fallback en installation utilisateur."
  echo "[facade2d] Détail venv:"
  cat /tmp/facade2d_venv.log || true
  rm -rf "${VENV_DIR}"
  python3 -m pip install --user --upgrade pip
  python3 -m pip install --user -e "${ROOT_DIR}"
fi

if [[ "${MODE}" == "venv" ]]; then
  cat <<'EOF'

Installation terminée.

Utilisation CLI:
  source .venv-facade2d/bin/activate
  facade2d process --input ./photo.jpg --output ./out

Utilisation API:
  source .venv-facade2d/bin/activate
  facade2d-api

EOF
else
  cat <<'EOF'

Installation terminée (mode user).

Utilisation CLI:
  python3 -m facade2d process --input ./photo.jpg --output ./out

Utilisation API:
  python3 -m facade2d.api

Si "facade2d" n'est pas trouvé, ajoute ~/.local/bin au PATH.

EOF
fi
