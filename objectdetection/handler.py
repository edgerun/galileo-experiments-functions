import tempfile
import time

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import numpy as np

modelUrl = "./function/model/model.tflite"

def handle(event, body):
    # load model
    start_time = time.time()
    try:
        base_options = core.BaseOptions(
            file_name=modelUrl, use_coral=False, num_threads=4)
        detection_options = processor.DetectionOptions(
            max_results=3, score_threshold=0.3)
        options = vision.ObjectDetectorOptions(
            base_options=base_options, detection_options=detection_options)
        detector = vision.ObjectDetector.create_from_options(options)
    except Exception as e:
        return returnBadRequest("Error while model loading: " + str(e))
    stop_time = time.time()
    model_load_time = stop_time - start_time

    # preprocess
    start_time = time.time()
    try:
        _, filename = tempfile.mkstemp(suffix=".jpg")
        nparr = np.fromstring(event.body, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_tensor = vision.TensorImage.create_from_array(rgb_image)
        stop_time = time.time()
    except Exception as e:
        return returnBadRequest("Error while pre-processing: " + str(e))
    preprocess_time = stop_time - start_time

    # predict
    start_time = time.time()
    try:
        result = detector.detect(input_tensor)
        stop_time = time.time()
    except Exception as e:
        return returnBadRequest("Error while inference: " + str(e))
    predict_time = stop_time - start_time

    # post process
    start_time = time.time()
    try:
        results_sorted = []
        for value in result.detections:
            for c in value.classes:
                results_sorted.append({
                    'score': c.score,
                    'category_name': c.class_name
                })
    except Exception as e:
        return returnBadRequest("Error while post-process: " + str(e))
    stop_time = time.time()
    post_process_time = stop_time - start_time

    return {
        "statusCode": 200,
        "body": {
            "model_load_time": model_load_time * 1000,
            "preprocess_time": preprocess_time * 1000,
            "predict_time": predict_time * 1000,
            "post_process_time": post_process_time * 1000,
            "results": results_sorted
        }
    }

def returnBadRequest(msg):
    return {
        "statusCode": 400,
        "body": msg
    }