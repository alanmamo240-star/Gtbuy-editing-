#!/bin/bash
# USFans versions of the talking-head videos v8 v9 v10 v12 v13
S=/tmp/claude-0/-home-user-Gtbuy-editing-/f9b90bf7-6ab1-5b45-a5b2-686521ff918d/scratchpad
US=$S/usvoice/take6.wav; KA=$S/klarna/take3.wav; KB=$S/klarna/take4.wav
prep() { # v enh
  cd $S/$1/work || return 1
  if [ "$1" = v12 ]; then
    [ -f input_full.mov ] || ffmpeg -v error -y -i ../src/input_raw.mov -vf fps=30 -c:v libx264 -crf 10 -preset medium -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 input_full.mov
    [ -f input.mov ] || ffmpeg -v error -y -i input_full.mov -filter_complex "[0:v]select='lt(n,648)+gte(n,747)',setpts=N/30/TB[v];[0:a]atrim=0:21.615,asetpts=PTS-STARTPTS[a1];[0:a]atrim=start=24.885,asetpts=PTS-STARTPTS[a2];[a1][a2]acrossfade=d=0.03:c1=tri:c2=tri[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 10 -preset medium -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 input.mov
  else
    [ -f input.mov ] || ffmpeg -v error -y -i ../src/input_raw.mov -vf fps=30 -c:v libx264 -crf 10 -preset medium -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 input.mov
  fi
  [ -f enh.mov ] || ffmpeg -v error -y -i input.mov -vf "$2" -an -c:v libx264 -crf 8 -preset medium -pix_fmt yuv420p enh.mov
  [ -f mask.mkv ] || { cp faces.json faces_old.json 2>/dev/null; python3 ../mask_track.py > mask.log 2>&1; }
}
render() { # v script post mix chunks br splices...
  v=$1; R=$2; P=$3; MIX=$4; CH=$5; BR=$6; shift 6
  cd $S/$v/work || return 1
  echo "=== $v render $(date +%T)"
  rm -f seg_*.mkv r_*.log; n=0
  for c in $CH; do a=${c%-*}; b=${c#*-}; python3 ../$R $a $b seg_$a.mkv > r_$a.log 2>&1 & n=$((n+1)); [ $((n % 2)) -eq 0 ] && wait; done; wait
  [ "$(grep -l '^done' r_*.log | wc -l)" -eq 4 ] || { echo "$v RENDER FAILED"; for f in r_*.log; do tail -n 4 $f; done; return 1; }
  python3 $P > post.log 2>&1 || { echo "$v POST FAILED"; tail -5 post.log; return 1; }
  python3 ../../splice_words.py $MIX mix_us.wav "$@" || { echo "$v SPLICE FAILED"; return 1; }
  ffmpeg -v error -y -i post.mkv -i mix_us.wav -map 0:v -map 1:a -af apad -c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -c:a aac -b:a 320k -shortest master_hq.mp4
  for p in 1 2; do ffmpeg -v error -y -i master_hq.mp4 -c:v libx264 -preset slow -b:v ${BR}M -maxrate $((BR+8))M -bufsize $((BR*2))M -pass $p -passlogfile p2 -profile:v high -level 4.2 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 $([ $p = 1 ] && echo "-an -f null /dev/null" || echo "-c:a copy -movflags +faststart usfans_$v.mp4"); done
  rm -f seg_*.mkv post.mkv master_hq.mp4
  echo "=== $v done $(date +%T) $(ffprobe -v error -show_entries format=duration -of csv=p=0 usfans_$v.mp4)"
}
case "$1" in
prep)
  prep v8 "hqdn3d=1.3:1.0:3.5:3.5,cas=0.38,eq=contrast=1.05:saturation=1.05:gamma=1.015,colorbalance=rs=-0.015:bs=0.025:rh=0.015:bh=-0.015"
  prep v9 "hqdn3d=1.3:1.0:3.5:3.5,cas=0.38,eq=contrast=1.05:saturation=1.04:gamma=1.015,colorbalance=rs=-0.015:bs=0.025:rh=0.01:bh=-0.01"
  prep v10 "hqdn3d=1.3:1.0:3.5:3.5,cas=0.38,eq=contrast=1.05:saturation=1.04:gamma=1.015,colorbalance=rs=-0.01:bs=0.02:rh=0.015:bh=-0.015"
  prep v12 "hqdn3d=1.3:1.0:3.5:3.5,cas=0.38,eq=contrast=1.05:saturation=1.04:gamma=1.015,colorbalance=rs=-0.01:bs=0.02:rh=0.01:bh=-0.01"
  echo PREPDONE ;;
all)
  render v8 render8_us.py post8.py mix.wav "0-273 273-546 546-819 819-1092" 18 "1.48:1.88:$US" "5.15:5.55:$US" "15.55:16.14:$US" "17.32:17.92:$KA"
  render v9 render9_us.py post9.py mix.wav "0-195 195-390 390-585 585-777" 20 "1.80:2.20:$KA" "3.24:3.70:$US" "6.10:6.62:$KB" "11.66:12.02:$KA"
  render v10 render10_us.py post10.py mix.wav "0-292 292-584 584-876 876-1167" 20 "18.47:19.04:$US"
  render v12 render12_us.py post12.py mix.wav "0-218 218-436 436-654 654-870" 20 "7.02:7.50:$US"
  render v13 render13_us.py post13.py mix2.wav "26-201 201-402 402-603 603-804" 20 "0.00:0.75:$US"
  echo ALLDONE ;;
v13only)
  render v13 render13_us.py post13.py mix2.wav "26-201 201-402 402-603 603-804" 20 "0.00:0.75:$US"
  echo V13DONE ;;
esac
