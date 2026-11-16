#!/bin/bash
# tools/queue.sh zug-3 zug-4 ...   -> waits for any running render, then renders + encodes each episode in turn (mix must exist)
ROOT=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
while pgrep -f "node tools/render[.]mjs" > /dev/null; do sleep 10; done
for EP in "$@"; do
  [ -f "$ROOT/$EP/audio/mix.wav" ] || { echo "$EP: no mix"; continue; }
  N=$(ls "$ROOT/$EP/frames" 2>/dev/null | wc -l); NEED=$(python3 -c "import json;print(round(json.load(open('$ROOT/$EP/timeline.json'))['duration']*30))")
  [ "$N" -ge "$NEED" ] || "$ROOT/tools/ep.sh" "$EP" render "${W:-2}"
  N=$(ls "$ROOT/$EP/frames" 2>/dev/null | wc -l); [ "$N" -ge "$NEED" ] || { echo "$EP: only $N of $NEED frames"; continue; }
  "$ROOT/tools/ep.sh" "$EP" encode && echo "$EP done"
done
