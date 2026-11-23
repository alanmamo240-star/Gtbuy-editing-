#!/bin/bash
S=/tmp/claude-0/-home-user-Gtbuy-editing-/f9b90bf7-6ab1-5b45-a5b2-686521ff918d/scratchpad
while pgrep -f rebrand_fit.sh >/dev/null; do sleep 10; done
cd $S/v4/work || exit 1
echo "=== v4 start $(date +%T)"
[ -f input.mov ] || ffmpeg -v error -y -i ../src/input_raw.mov -vf fps=30 -c:v libx264 -crf 10 -preset medium -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 input.mov
[ -f enh.mov ] || ffmpeg -v error -y -i input.mov -vf "hqdn3d=1.3:1.0:3.5:3.5,cas=0.38,eq=contrast=1.05:saturation=1.05:gamma=1.015,colorbalance=rs=-0.015:bs=0.025:rh=0.015:bh=-0.015" -an -c:v libx264 -crf 8 -preset medium -pix_fmt yuv420p enh.mov
[ -f mask.mkv ] || python3 ../mask_track.py > mask.log 2>&1
cp ../render4_us.py .; rm -f seg_*.mkv r_*.log
n=0; for c in 0-272 272-544 544-816 816-1087; do a=${c%-*}; b=${c#*-}; python3 render4_us.py $a $b seg_$a.mkv > r_$a.log 2>&1 & n=$((n+1)); [ $((n % 3)) -eq 0 ] && wait; done; wait
[ "$(grep -l '^done' r_*.log | wc -l)" -eq 4 ] || { echo "v4 RENDER FAILED"; for f in r_*.log; do tail -n 3 $f; done; exit 1; }
python3 ../../mute_words.py mix.wav mix_us.wav 9.74:10.44
ffmpeg -v error -y -i seg_0.mkv -i seg_272.mkv -i seg_544.mkv -i seg_816.mkv -i mix_us.wav -filter_complex "[0:v][1:v][2:v][3:v]concat=n=4:v=1:a=0,setpts=N/30/TB[v]" -map "[v]" -map 4:a -c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -c:a aac -b:a 320k master_hq.mp4
for p in 1 2; do ffmpeg -v error -y -i master_hq.mp4 -c:v libx264 -preset slow -b:v 18M -maxrate 26M -bufsize 36M -pass $p -passlogfile p2 -profile:v high -level 4.2 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 $([ $p = 1 ] && echo "-an -f null /dev/null" || echo "-c:a copy -movflags +faststart usfans_v4.mp4"); done
rm -f seg_*.mkv master_hq.mp4
echo "=== v4 done $(date +%T) $(ffprobe -v error -show_entries format=duration -of csv=p=0 usfans_v4.mp4)"
