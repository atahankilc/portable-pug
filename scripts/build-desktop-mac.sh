#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== 1/4  Building Django sidecar with PyInstaller ==="
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
  echo "Error: backend/venv not found. Create a virtualenv and install requirements first."
  exit 1
fi
source venv/bin/activate
pip install pyinstaller --quiet
pyinstaller pyinstaller.spec --noconfirm --clean
deactivate

echo "=== 2/4  Exporting Expo web build ==="
cd "$ROOT_DIR/frontend"
npx expo export --platform web

echo "=== 3/4  Copying resources into desktop/ ==="
cd "$ROOT_DIR/desktop"
rm -rf resources/sidecar resources/web
mkdir -p resources/sidecar resources/web

# PyInstaller COLLECT output is a directory
cp -R "$ROOT_DIR/backend/dist/run_server/"* resources/sidecar/
cp -R "$ROOT_DIR/frontend/dist/"* resources/web/

echo "=== 4/4  Packaging with electron-builder ==="
npm install
npm run pack:mac

echo ""
echo "Done! Output is in desktop/release/"
