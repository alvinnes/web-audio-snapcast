#!/bin/bash

echo "Start Music..."

pkill -9 ffmpeg 2>/dev/null
sleep 0.5

[ ! -p /tmp/snapfifo ] && mkfifo /tmp/snapfifo
chmod 666 /tmp/snapfifo

exec ffmpeg -y -nostdin -loglevel warning -re -stream_loop -1 \
  -i /home/eksan/music/SOS1.mp3 \
  -af "aresample=48000:resampler=soxr" \
  -ac 2 -ar 48000 \
  -f s16le \
  /tmp/snapfifo
