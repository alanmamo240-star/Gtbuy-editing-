"""Person+hair matte (MediaPipe selfie multiclass, temporally smoothed) + per-frame face box (BlazeFace)."""
import cv2, numpy as np, mediapipe as mp, subprocess, json
from mediapipe.tasks.python import vision, BaseOptions
W,H,FPS=1080,1920,30
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path="models/selfie_multiclass_256x256.tflite"),
    running_mode=vision.RunningMode.VIDEO,output_confidence_masks=True))
fd=vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path="models/blaze_face_short_range.tflite"),
    running_mode=vision.RunningMode.VIDEO,min_detection_confidence=0.4))
dec=subprocess.Popen(["ffmpeg","-v","error","-i","input.mov","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","gray","-s",f"{W}x{H}","-r","30","-i","-","-c:v","ffv1","mask.mkv"],stdin=subprocess.PIPE)
prev=None;i=0;faces=[]
while True:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    f=np.ascontiguousarray(np.frombuffer(b,np.uint8).reshape(H,W,3))
    img=mp.Image(image_format=mp.ImageFormat.SRGB,data=f); ts=int(i*1000/FPS)
    r=seg.segment_for_video(img,ts)
    bg=r.confidence_masks[0].numpy_view()
    m=cv2.resize(1-bg,(W,H),interpolation=cv2.INTER_LINEAR)
    m=cv2.GaussianBlur(m,(0,0),1.6); m=np.clip((m-0.35)/0.3,0,1)
    if prev is not None: m=0.65*m+0.35*prev
    prev=m
    enc.stdin.write((m*255).astype(np.uint8).tobytes())
    d=fd.detect_for_video(img,ts)
    if d.detections:
        bb=max(d.detections,key=lambda x:x.categories[0].score).bounding_box
        faces.append([i,bb.origin_x,bb.origin_y,bb.width,bb.height])
    else: faces.append([i,None,None,None,None])
    i+=1
enc.stdin.close(); enc.wait(); json.dump(faces,open("faces.json","w")); print("frames",i,"faces",sum(1 for x in faces if x[1] is not None))
