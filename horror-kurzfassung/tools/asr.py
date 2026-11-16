# python3 tools/asr.py   (run in horror-kurzfassung/; needs pip install faster-whisper)
# Word timestamps for every Nixly recording -> nixly/asr.json, which tools/splitall.py uses to cut the lines.
import json, os, sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8', download_root=os.environ.get('WHISPER_DIR', os.path.expanduser('~/.cache/whisper')))
D = 'nixly/'
out = {}
for v in json.load(open(D + 'files.json')):
    au = np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',D+v+'.mp3','-ar','16000','-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout, np.float32)
    segs, _ = m.transcribe(au, language='de', word_timestamps=True, beam_size=5, vad_filter=False)
    ws = [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for s in segs for w in s.words]
    out[v] = ws; print(v, ' '.join(f'{w}[{a}-{b}]' for w, a, b in ws), flush=True)
json.dump(out, open(D + 'asr.json', 'w'), ensure_ascii=False, indent=0)
