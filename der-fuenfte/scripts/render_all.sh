#!/bin/bash
cd "$(dirname "$0")"
for n in 1 2 3 4; do
  rm -f ep${n}_chunk_*.mp4
  for k in 0 1 2 3; do python3 show.py $n chunk $k 4 > r${n}_$k.log 2>&1 & done
  wait
  printf "file 'ep${n}_chunk_0.mp4'\nfile 'ep${n}_chunk_1.mp4'\nfile 'ep${n}_chunk_2.mp4'\nfile 'ep${n}_chunk_3.mp4'\n" > ep${n}_concat.txt
  ffmpeg -v error -y -f concat -safe 0 -i ep${n}_concat.txt -i ep${n}_audio.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a aac -b:a 192k -movflags +faststart -shortest ep${n}_final.mp4
  echo "EP $n FINISHED $(date +%T)" >> render_all.log
done
echo ALL_DONE >> render_all.log
