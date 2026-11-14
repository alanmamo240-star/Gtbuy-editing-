import subprocess, numpy as np, cv2
W,H=270,480
p=subprocess.Popen(["ffmpeg","-v","error","-i","input.mov","-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
prev=None;i=0;rows=[]
while True:
    b=p.stdout.read(W*H)
    if len(b)<W*H: break
    g=np.frombuffer(b,np.uint8).reshape(H,W).astype(np.float32)
    sh=cv2.Laplacian(g[60:300],cv2.CV_32F).var()
    d=0 if prev is None else np.abs(g-prev).mean()
    rows.append((i/30,sh,d));prev=g;i+=1
a=np.array(rows);med=np.median(a[:,1])
print("median sharp",med)
for t,s,d in a:
    if s<med*0.45 or d>12: print(f"{t:6.2f} sharp={s:7.1f} diff={d:5.1f}")
np.save("sharp.npy",a)
