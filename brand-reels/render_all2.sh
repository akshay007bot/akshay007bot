#!/bin/bash
R=../.claude/skills/motion-reel/scripts
for f in vedrx-story annova-3d ioceane-split mrcomm-city; do
  echo "=== $f $(date +%T)"
  node $R/render.mjs --film $f --format 9x16 --video-only 2>&1 | tr '\r' '\n' | tail -1
  node $R/sfx.mjs $f 2>&1 | tail -1; node $R/mix.mjs $f 2>&1 | tail -2
  node $R/render.mjs --film $f --poster 28.5 --format 9x16 2>&1 | tail -1
done; echo "ALL DONE $(date +%T)"
