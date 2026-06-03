#!/bin/bash

echo "Paging ON..."

pkill -9 ffmpeg 2>/dev/null
sleep 0.5

/usr/bin/ffmpeg -y -nostdin \
-f alsa -i plughw:1,0 \
-af "volume=3.0,aresample=48000:resampler=soxr" \
-ac 2 -ar 48000 \
-f s16le \
/tmp/snapfifo
