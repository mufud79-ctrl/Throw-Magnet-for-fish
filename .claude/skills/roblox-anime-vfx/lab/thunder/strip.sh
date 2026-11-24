#!/bin/sh
# Dense frame strip around a beat: strip.sh <video.mp4> <start_s> <end_s> <out.jpg> [cols=6] [width=320]
# Every frame between start and end (30 fps), tiled with the frame time burned in.
V=$1; A=$2; B=$3; O=$4; C=${5:-6}; W=${6:-320}
N=$(python3 -c "import math;print(max(1,round(($B-$A)*30)))")
R=$(( (N + C - 1) / C ))
ffmpeg -y -loglevel error -ss "$A" -t "$(python3 -c "print($B-$A)")" -i "$V" -frames:v 1 -vf "drawtext=text='%{pts\:flt\:$A}':x=6:y=6:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.5,scale=$W:-1,tile=${C}x${R}" "$O"
