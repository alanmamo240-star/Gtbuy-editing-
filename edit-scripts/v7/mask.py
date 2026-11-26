# Person matte (MediaPipe selfie multiclass) + head-top / head-centre tracking. Writes mask.mkv, head.npy (top_y, cx)
import cv2, numpy as np, mediapipe as mp, subprocess
from mediapipe.tasks.python import vision, BaseOptions
W,H=1080,1920
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path="seg.tflite"),running_mode=vision.RunningMode.VIDEO,output_confidence_masks=True))
dec=subprocess.Popen(["ffmpeg","-v","error","-i","input_cfr.mov","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","gray","-s",f"{W}x{H}","-r","30","-i","-","-c:v","ffv1","mask.mkv"],stdin=subprocess.PIPE)
prev=None;i=0;HD=[]
while True:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    f=np.frombuffer(b,np.uint8).reshape(H,W,3)
    r=seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(f)),int(i*1000/30))
    bg=r.confidence_masks[0].numpy_view()
    m=cv2.resize(1-bg,(W,H),interpolation=cv2.INTER_LINEAR)
    m=cv2.GaussianBlur(m,(0,0),2.0); m=np.clip((m-0.35)/0.3,0,1)
    if prev is not None: m=0.6*m+0.4*prev
    prev=m
    rows=np.where((m>0.5).sum(1)>12)[0]; top=rows.min() if len(rows) else 700
    band=m[top:top+160]>0.5; xs=np.where(band.any(0))[0]; cx=(xs.min()+xs.max())/2 if len(xs) else 540
    HD.append((top,cx))
    enc.stdin.write((m*255).astype(np.uint8).tobytes()); i+=1
enc.stdin.close(); enc.wait(); np.save("head.npy",np.array(HD,np.float32)); print("frames",i)
