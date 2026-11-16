#!/bin/bash
# Mix score + VO (offsets from src/timeline.json) and mux onto the rendered video.
# usage: ./mix.sh in.mp4 out.mp4
set -e; cd "$(dirname "$0")"
read -r -a OFF <<< "$(python3 -c "import json;t=json.load(open('src/timeline.json'));print(' '.join(str(t['vo'][k]/30) for k in ['v1','v2','v3','v4','v5','v6','v7']))")"
TOTAL=$(python3 -c "import json;print(json.load(open('src/timeline.json'))['total']/30)")
inputs="-i $1 -i public/audio/score.wav"; f="[1:a]volume=0.5,atrim=0:$TOTAL[m];"; mixin="[m]"
for i in 1 2 3 4 5 6 7; do
  inputs="$inputs -i public/audio/v$i.wav"; ms=$(python3 -c "print(int(${OFF[$((i-1))]}*1000))")
  f="$f[$((i+1)):a]adelay=${ms}|${ms},apad[v$i];"; mixin="$mixin[v$i]"
done
# duck the score under VO with sidechain compression
f="${f}[v1][v2][v3][v4][v5][v6][v7]amix=inputs=7:normalize=0,atrim=0:$TOTAL,asplit[vo][sc];[m][sc]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[md];[md][vo]amix=inputs=2:normalize=0,afade=t=out:st=$(python3 -c "print($TOTAL-0.7)"):d=0.7,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
f=$(echo "$f" | sed 's/\[m\]\[v1\]\[v2\]/[v1][v2]/')
ffmpeg -y -v error $inputs -filter_complex "$f" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$2"
