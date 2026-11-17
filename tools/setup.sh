#!/bin/bash
# One-time setup on a new Mac / Linux machine. Run from the project root:  bash tools/setup.sh
set -e
need() { command -v "$1" >/dev/null || { echo "MISSING: $1  -> $2"; MISSING=1; }; }
need node   "install Node.js 20+ from https://nodejs.org"
need ffmpeg "mac: brew install ffmpeg   ubuntu: sudo apt install ffmpeg"
need uv     "curl -LsSf https://astral.sh/uv/install.sh | sh"
[ -n "$MISSING" ] && { echo "Install the missing tools above, then run this again."; exit 1; }
cd brand-reels && npm install && npx playwright install chromium && cd ..
echo "Setup done. Open this folder in Claude Code and ask for a reel or carousel (see README_START_HERE.md)."
