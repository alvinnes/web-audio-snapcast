#!/bin/bash

while true; do
  ffmpeg -re -stream_loop -1 \
    -i /home/eksan/music/Album1.mp3 \
    -af "aresample=48000:resampler=soxr" \
    -ac 2 -ar 48000 \
    -f s16le \
    /tmp/snapfifo
done
