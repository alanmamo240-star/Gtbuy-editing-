#!/bin/bash
# Run a tool for one episode folder. Each episode is served by its own local web server.
#   tools/ep.sh zug-2 snap info|beats|range a b|<times>     -> snapshots / beat table   (env SCALE, NOTIMINGS)
#   Voices for zug-2..4 and stadt-1..4 (run in horror-kurzfassung/): one Nixly recording per speaker in nixly/ (see
#   voices_all.json), then python3 tools/asr.py (word times) and python3 tools/splitall.py -> every episode's lines + timings.json
#   tools/ep.sh zug-2 tts            -> old local German voices (Piper), only as a fallback
#   tools/ep.sh zug-2 mix            -> audio/mix.wav (voices, story effects, Nixly music; no camera whooshes)
#   tools/ep.sh zug-2 remux          -> swap the audio of the finished mp4 for audio/mix.wav
#   tools/ep.sh zug-2 render [N]     -> frames/ with N workers (default 2), resumable
#   tools/ep.sh zug-2 encode         -> ../der_zug_ohne_morgen_folge2.mp4
#   tools/ep.sh zug-2 all            -> snap info, tts, snap info, mix, render, encode
ROOT=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd); EP=$1; shift; cd "$ROOT/$EP" || exit 1
case $EP in zug-*) PORT=$((8200 + ${EP#zug-})); OUT="der_zug_ohne_morgen_folge${EP#zug-}.mp4";;
            stadt-*) PORT=$((8210 + ${EP#stadt-})); OUT="die_stadt_hinter_der_sperre_folge${EP#stadt-}.mp4";; *) PORT=8299; OUT="$EP.mp4";; esac
STORY=${STORY:-$(echo "$EP" | tr -d '-')}; export STORY PORT
for f in index.html src node_modules tools; do [ -e "$f" ] || ln -s "../$f" "$f"; done
if ! curl -s -o /dev/null "http://localhost:$PORT/index.html"; then
  (nohup npx http-server -p "$PORT" -s -c-1 . >/dev/null 2>&1 &)
  for i in $(seq 1 40); do curl -s -o /dev/null "http://localhost:$PORT/index.html" && break; sleep 0.5; done
fi
cmd=$1; shift
case $cmd in
  snap)   node tools/snap.mjs "$@" 2>&1 | grep -v 'status of 404'; true ;;
  tts)    python3 tools/tts.py ;;
  voice)  python3 tools/voice.py ;;
  mix)    python3 tools/mix2.py ;;
  remux)  T=$(mktemp --suffix=.mp4 -p .) && ffmpeg -v error -y -i "../$OUT" -i audio/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart "$T" && mv "$T" "../$OUT" && ffprobe -v error -show_entries format=duration -of csv=p=0 "../$OUT" ;;
  render) W=${1:-2}; for i in $(seq 0 $((W - 1))); do node tools/render.mjs "$i" "$W" > "r$i.log" 2>&1 & done; wait; tail -n 1 r*.log ;;
  encode) ffmpeg -v error -y -framerate 30 -i frames/f%05d.jpg -i audio/mix.wav -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -tune animation -movflags +faststart -c:a aac -b:a 256k -shortest "../$OUT" && ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,duration -of csv=p=0 "../$OUT" ;;
  all)    node tools/snap.mjs info > /dev/null 2>&1; python3 tools/tts.py && node tools/snap.mjs info 2>&1 | head -2 && python3 tools/mix2.py && "$0" "$EP" render "${1:-2}" && "$0" "$EP" encode ;;
  *)      "$cmd" "$@" ;;
esac
