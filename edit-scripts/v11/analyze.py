"""matte + pose landmarks + face per frame"""
import cv2, numpy as np, mediapipe as mp, subprocess, json
from mediapipe.tasks.python import vision, BaseOptions
W,H,FPS=1080,1920,30
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path="models/selfie_multiclass_256x256.tflite"),
    running_mode=vision.RunningMode.VIDEO,output_confidence_masks=True))
pose=vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="models/pose_landmarker_full.task"),
    running_mode=vision.RunningMode.VIDEO,min_pose_detection_confidence=0.4,min_tracking_confidence=0.4))
dec=subprocess.Popen(["ffmpeg","-v","error","-i","input.mov","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","gray","-s",f"{W}x{H}","-r","30","-i","-","-c:v","ffv1","mask.mkv"],stdin=subprocess.PIPE)
prev=None;i=0;P=[]
CUTS={36,77,132,181,238,271,334}
while True:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    f=np.ascontiguousarray(np.frombuffer(b,np.uint8).reshape(H,W,3))
    img=mp.Image(image_format=mp.ImageFormat.SRGB,data=f); ts=int(i*1000/FPS)
    r=seg.segment_for_video(img,ts)
    m=cv2.resize(1-r.confidence_masks[0].numpy_view(),(W,H),interpolation=cv2.INTER_LINEAR)
    m=cv2.GaussianBlur(m,(0,0),1.6); m=np.clip((m-0.35)/0.3,0,1)
    if prev is not None and i not in CUTS: m=0.65*m+0.35*prev
    prev=m
    enc.stdin.write((m*255).astype(np.uint8).tobytes())
    pr=pose.detect_for_video(img,ts)
    P.append([[l.x*W,l.y*H,l.visibility] for l in pr.pose_landmarks[0]] if pr.pose_landmarks else None)
    i+=1
enc.stdin.close(); enc.wait(); json.dump(P,open("pose.json","w")); print("frames",i,"pose",sum(p is not None for p in P))
