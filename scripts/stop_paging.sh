#!/bin/bash

echo "=== STOP PAGING ==="

pkill -9 ffmpeg 2>/dev/null

echo "Paging Stopped"