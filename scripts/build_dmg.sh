#!/usr/bin/env bash
# Build the .app then wrap it in a drag-to-Applications DMG.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  echo "no .venv — run: python3 -m venv .venv && .venv/bin/pip install -e '.[dist]'"
  exit 1
fi

.venv/bin/pip install --quiet 'py2app>=0.28' || true

rm -rf build dist
.venv/bin/python scripts/build_app.py py2app

if [ ! -d "dist/Octavius.app" ]; then
  echo "build failed — Octavius.app not found in dist/"
  exit 1
fi

# Build a simple drag-to-Applications DMG
DMG_NAME="dist/Octavius-0.1.0.dmg"
mkdir -p dist/dmg_staging
cp -R dist/Octavius.app dist/dmg_staging/
ln -sf /Applications dist/dmg_staging/Applications

hdiutil create -volname "Octavius" \
  -srcfolder dist/dmg_staging \
  -ov -format UDZO \
  "$DMG_NAME"

rm -rf dist/dmg_staging
echo
echo "Built: $DMG_NAME"
echo "Test:  open $DMG_NAME"
echo
echo "NOTE: unsigned. First-time users right-click → Open to bypass Gatekeeper."
