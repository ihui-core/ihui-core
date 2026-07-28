#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
DOCENGINE_PROJECTBRAIN=${DOCENGINE_PROJECTBRAIN:-$HOME/Proyectos/ihui-notarias/PROJECTBRAIN} \
  python docengine/generate.py
cd docengine/dashboard && npm run build
echo "[OK] Dashboard actualizado."
