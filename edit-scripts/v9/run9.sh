#!/bin/bash
# render 6 chunks, 3 at a time (memory), then concat + mix audio
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for g in "0 1 2" "3 4 5"; do
  for k in $g; do python3 render9.py chunk $k 6 > log_$k.txt 2>&1 & done; wait
done
printf "file 'chunk_%d.mp4'\n" 0 1 2 3 4 5 > chunks.txt
ffmpeg -v error -y -f concat -safe 0 -i chunks.txt -c copy video_only.mp4
DUR=$(python3 -c "from tl import DUR;print(DUR)")
ffmpeg -v error -y -i video_only.mp4 -i voice_cut.wav -i music.wav -i sfx.wav -filter_complex \
"[1:a]highpass=f=75,afftdn=nr=8:nf=-40:tn=1,equalizer=f=3500:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=2.8:attack=12:release=180:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=8,aresample=48000,asplit=2[v][vsc];\
[2:a]volume=-19dB[mu];[mu][vsc]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=450[mud];\
[3:a]volume=0dB[sx];[v][mud][sx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.9,afade=t=out:st=$(python3 -c "print($DUR-0.35)"):d=0.35[a]" \
-map 0:v -map "[a]" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
-c:a aac -b:a 256k -movflags +faststart -shortest out_v9.mp4
echo ALLDONE
