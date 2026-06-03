#!/bin/bash

echo "=== STOP MUSIC ==="

pkill -9 ffmpeg 2>/dev/null
pkill -9 yt-dlp 2>/dev/null

echo "Music Stopped"