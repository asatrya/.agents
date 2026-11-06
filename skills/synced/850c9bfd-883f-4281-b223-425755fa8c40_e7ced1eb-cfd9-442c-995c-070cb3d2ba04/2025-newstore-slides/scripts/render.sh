#!/usr/bin/env bash
# render.sh — build a NewStore deck, validate it, and render slides to JPGs for visual QA.
# Usage:  bash render.sh <build.js> <output.pptx> [dpi]
#
# Why this exists: in the Cowork sandbox the output folder is a host mount that
# BLOCKS overwriting a file that already exists. Re-rendering to the same PDF/JPG
# names silently keeps the STALE image. This script always renders to a FRESH,
# timestamped name so previews reflect the latest build. Read the printed JPG paths.
set -e
BUILD="${1:?usage: render.sh build.js output.pptx [dpi]}"
PPTX="${2:?usage: render.sh build.js output.pptx [dpi]}"
DPI="${3:-120}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PPTX_SKILL="/sessions/$(ls /sessions 2>/dev/null | head -1)/mnt/.claude/skills/pptx"
[ -d "$PPTX_SKILL" ] || PPTX_SKILL="$(find / -maxdepth 8 -type d -name pptx -path '*skills*' 2>/dev/null | head -1)"

export NODE_PATH="${NODE_PATH:-/usr/local/lib/node_modules_global/lib/node_modules}"

# Icon set for NS.icons() — lucide-static SVGs (sharp is already global). Installed once
# to a stable location and added to NODE_PATH so icon rendering works automatically.
ICONLIB="$HOME/.ns-icons"
if ! node -e "require('lucide-static')" 2>/dev/null; then
  mkdir -p "$ICONLIB"; ( cd "$ICONLIB" && npm init -y >/dev/null 2>&1; npm install lucide-static >/dev/null 2>&1 ) || true
fi
export NODE_PATH="$NODE_PATH:$ICONLIB/node_modules"

echo "== build =="
node "$BUILD"

echo "== validate =="
python "$PPTX_SKILL/scripts/office/validate.py" "$PPTX" 2>&1 | tail -3 || true

echo "== placeholder scan (excluding intentional ~\$XXX source markers) =="
markitdown "$PPTX" 2>/dev/null | grep -iE "lorem|ipsum|\bTODO|\[insert|this.*(page|slide).*layout" || echo "  none"

TAG=$(date +%s%N | tail -c 7)
DIR="$(cd "$(dirname "$PPTX")" && pwd)"   # absolute, so --outdir is unambiguous
cp "$PPTX" "$DIR/_qa_$TAG.pptx"
# --outdir forces the PDF next to the pptx; without it soffice writes to CWD/$HOME
python "$PPTX_SKILL/scripts/office/soffice.py" --headless --convert-to pdf --outdir "$DIR" "$DIR/_qa_$TAG.pptx" >/dev/null 2>&1
[ -f "$DIR/_qa_$TAG.pdf" ] || { echo "PDF not produced — check LibreOffice"; exit 1; }
pdftoppm -jpeg -r "$DPI" "$DIR/_qa_$TAG.pdf" "$DIR/_qa_$TAG"
echo "== preview JPGs (read these) =="
ls -1 "$DIR"/_qa_$TAG-*.jpg
