#!/bin/bash
# sheet.sh <brand> <out.png>: all slides side by side at 360px
d=$1/final; files=($(ls $d/*_Carousel_*.png)); n=${#files[@]}; args=""; f=""
for i in "${!files[@]}"; do args="$args -i ${files[$i]}"; f="$f[$i]scale=360:450[v$i];"; done
for i in "${!files[@]}"; do f="$f[v$i]"; done
ffmpeg -loglevel error -y $args -filter_complex "${f}hstack=$n" $2
