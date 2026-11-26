from faster_whisper import WhisperModel
import json, numpy as np, wave
w=wave.open("audio.wav");audio=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
m=WhisperModel("large-v3-turbo",device="cpu",compute_type="int8")
segs,info=m.transcribe(audio,language="de",word_timestamps=True,vad_filter=True)
out=[];print(info.language)
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words: out.append(dict(w=w.word.strip(),s=w.start,e=w.end))
json.dump(out,open("words.json","w"),ensure_ascii=False,indent=0)
