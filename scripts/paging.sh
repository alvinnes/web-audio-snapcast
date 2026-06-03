#!/bin/bash

echo "🔊 Paging Mic Aktif..."

# Stop music
pkill -f music.sh
pkill -f ffmpeg

# Delay kecil biar FIFO clear
sleep 1

# Kirim mic ke semua speaker
ffmpeg -f alsa -i default \
  -af "aresample=48000:resampler=soxr" \
  -ac 2 -ar 48000 \
  -f s16le \
  /tmp/snapfifo

echo "🔚 Paging selesai, kembali ke musik"

# Restart music
/home/eksan/music.sh &
