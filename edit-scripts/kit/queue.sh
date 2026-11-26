#!/bin/bash
# run renders one after another: wait for previous out.mp4
for d in "$@"; do
  while pgrep -f "render.py chunk" >/dev/null || pgrep -f "run.sh" >/dev/null; do sleep 5; done
  (cd $d && ./run.sh > run.log 2>&1)
done
