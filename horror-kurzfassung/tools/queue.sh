#!/bin/bash
# tools/queue.sh zug-3 zug-4 ...   -> waits for any running render, then renders + encodes each episode in turn (mix must exist)
ROOT=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
while pgrep -f "node tools/render[.]mjs" > /dev/null; do sleep 10; done
for EP in "$@"; do
  [ -f "$ROOT/$EP/audio/mix.wav" ] || { echo "$EP: no mix"; continue; }
  N=$(ls "$ROOT/$EP/frames" 2>/dev/null | wc -l)
  [ "$N" -ge 900 ] || "$ROOT/tools/ep.sh" "$EP" render 2
  "$ROOT/tools/ep.sh" "$EP" encode && echo "$EP done"
done
