#!/bin/bash
while pgrep -f rebrand_v4.sh >/dev/null; do sleep 10; done
S=/tmp/claude-0/-home-user-Gtbuy-editing-/f9b90bf7-6ab1-5b45-a5b2-686521ff918d/scratchpad
run() { # v render post enh chunks par br
  v=$1; R=$2; P=$3; ENH=$4; CH=$5; PAR=$6; BR=$7
  cd $S/$v/work || return 1
  echo "=== $v start $(date +%T)"
  [ -f input.mov ] || ffmpeg -v error -y -i ../src/input_raw.mov -vf fps=30 -c:v libx264 -crf 10 -preset medium -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 input.mov
  [ -f enh.mov ] || ffmpeg -v error -y -i input.mov -vf "$ENH" -an -c:v libx264 -crf 8 -preset medium -pix_fmt yuv420p enh.mov
  [ -f mask.mkv ] || python3 ../analyze.py > an.log 2>&1
  cp ../$R ../$P .
  if [ "$(grep -l '^done' r_*.log 2>/dev/null | wc -l)" -ne 4 ]; then
    rm -f seg_*.mkv r_*.log; n=0
    for c in $CH; do a=${c%-*}; b=${c#*-}; python3 $R $a $b seg_$a.mkv > r_$a.log 2>&1 & n=$((n+1)); [ $((n % PAR)) -eq 0 ] && wait; done; wait
  fi
  [ "$(grep -l '^done' r_*.log | wc -l)" -eq 4 ] || { echo "$v RENDER FAILED"; for f in r_*.log; do tail -n 3 $f; done; return 1; }
  python3 $P > post.log 2>&1 || { echo "$v POST FAILED"; return 1; }
  ffmpeg -v error -y -i post.mkv -i mix.wav -map 0:v -map 1:a -af apad -c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -c:a aac -b:a 320k -shortest master_hq.mp4
  for p in 1 2; do ffmpeg -v error -y -i master_hq.mp4 -c:v libx264 -preset slow -b:v ${BR}M -maxrate $((BR+8))M -bufsize $((BR*2))M -pass $p -passlogfile p2 -profile:v high -level 4.2 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 $([ $p = 1 ] && echo "-an -f null /dev/null" || echo "-c:a copy -movflags +faststart usfans_$v.mp4"); done
  rm -f seg_*.mkv post.mkv master_hq.mp4
  echo "=== $v done $(date +%T) $(ffprobe -v error -show_entries format=duration -of csv=p=0 usfans_$v.mp4)"
}
#run v5 render5.py post5.py "hqdn3d=1.4:1.1:3.5:3.5,cas=0.40,eq=contrast=1.06:saturation=1.04:gamma=1.0,colorbalance=rs=-0.02:bs=0.03:rh=0.02:bh=-0.02" "0-94 94-188 188-282 282-375" 2 20
run v6 render6.py post6.py "hqdn3d=1.4:1.1:3.5:3.5,cas=0.40,eq=contrast=1.06:saturation=1.03,colorbalance=rs=-0.015:bs=0.02:rh=0.025:gh=0.01:bh=-0.025" "0-124 124-248 248-372 372-495" 2 20
run v7 render7.py post7.py "hqdn3d=1.4:1.1:3.5:3.5,cas=0.42,eq=contrast=1.07:saturation=1.02:gamma=1.0,colorbalance=rs=-0.02:bs=0.03:rh=0.015:bh=-0.015" "0-115 115-230 230-345 345-459" 3 20
run v11 render11.py post11.py "hqdn3d=1.4:1.1:3.5:3.5,cas=0.42,eq=contrast=1.08:saturation=0.92:gamma=1.0" "0-105 105-210 210-315 315-420" 3 20
echo ALLDONE
