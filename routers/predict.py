import os
from fastapi import APIRouter, HTTPException, UploadFile, File
import onnxruntime as ort
import numpy as np
import time
import torch
import onnx
from ultralytics.utils.ops import non_max_suppression
import matplotlib.pyplot as plt
from tqdm import tqdm
import ast
from PIL import Image
from moviepy.editor import VideoFileClip
from models.predict_request import PredictRequestModel
import uuid
import requests
router = APIRouter()

model_path = os.path.join("onnx_model",[f for f in os.listdir("onnx_model") if f.endswith(".onnx")][0])
print(f"Loading model from {model_path}")
model = onnx.load(model_path) 
class_dict = ast.literal_eval(model.metadata_props[-1].value)
del model

sess = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider','CPUExecutionProvider'])

def predict_frame(array: np.ndarray):
    img = Image.fromarray(array)
    img = img.resize((640, 640))
    img = np.array(img)
    img = np.expand_dims(img, axis=0)
    img = img.transpose((0, 3, 1, 2))
    img = (img/255.0).astype(np.float32)

    results_ort = sess.run(["output0"], {"images": img})
    result_nmp = non_max_suppression(torch.from_numpy(results_ort[0]),conf_thres=0.5)[0]
    boxes = [{
        'xMin': int(box[0])/640,
        'yMin': int(box[1])/640,
        'xMax': int(box[2])/640,
        'yMax': int(box[3])/640,'confidence': float(box[4]), 'class': class_dict[int(box[5])], 'classId':int(box[5])} for box in result_nmp]
    #rescale boxes to ratio of image
    return boxes




@router.post("/api/predict")
def predict(body: PredictRequestModel):
    video_id = str(uuid.uuid4())
    try:
        if body.url.endswith("/"):
            body.url = body.url[:-1]
        file = requests.get(body.url)
        with open(f"temp-{video_id}.mp4", 'wb') as f:
            f.write(file.content)
        clip = VideoFileClip(f"temp-{video_id}.mp4")
        if body.prediction_fps == None:
            body.prediction_fps = clip.fps
        result = []
        frame_count = 0
        prediction_count = 0
        predicted_frames_idx = np.arange(0,clip.fps*clip.duration,clip.fps/body.prediction_fps).astype(int)
        #print(predicted_frames_idx)
        for frame_idx,frame in tqdm(enumerate(clip.iter_frames()),total=int(clip.fps*clip.duration)):
            frame_count += 1
            if frame_idx not in predicted_frames_idx:
                continue
            prediction_count += 1
            prediction = predict_frame(frame)
            if len(prediction) > 0:
                result.append({'frame': frame_idx,'time':frame_idx/clip.fps, 'prediction': prediction})
        print(f"Predicted {prediction_count} frames out of {frame_count} frames")
        response = {'metadata':{
            'filename': f'{body.url.split("/")[-1]}',
            'video_fps': clip.fps,
            'prediction_fps': body.prediction_fps,
            'duration': clip.duration,
            'total_frames': frame_count
        },'result': result}
        clip.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(f"temp-{video_id}.mp4")
    return response