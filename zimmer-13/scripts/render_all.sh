#!/bin/bash
# Needs: pip install piper-tts opencv-python-headless scipy pillow numpy; ffmpeg with rubberband.
# Piper voices de_DE-{kerstin-low,ramona-low,eva_k-x_low}.onnx in $VOICES (default ./voices).
set -e; cd "$(dirname "$0")"
python3 tts.py && python3 mix.py
ffmpeg -v error -y -i build/audio_raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 build/audio.wav
rm -f build/chunk_*.mp4; for k in 0 1 2 3; do python3 render.py chunk $k 4 > build/r$k.log 2>&1 & done; wait
printf "file 'chunk_0.mp4'\nfile 'chunk_1.mp4'\nfile 'chunk_2.mp4'\nfile 'chunk_3.mp4'\n" > build/concat.txt
cd build
ffmpeg -v error -y -f concat -safe 0 -i concat.txt -c:v libx264 -preset slow -b:v 3800k -pass 1 -passlogfile p -an -f null /dev/null
ffmpeg -v error -y -f concat -safe 0 -i concat.txt -i audio.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 3800k -pass 2 -passlogfile p -maxrate 7M -bufsize 14M \
  -profile:v high -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest ../../zimmer13_folge1.mp4
