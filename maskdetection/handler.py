import time

from tflite_runtime.interpreter import Interpreter
import cv2
import numpy as np

# based on https://github.com/danieldanuega/mask-detector

def handle(event, context):
    maskModel = "./function/model/detect.tflite"
    pathLabels = "./function/model/labels.txt"

    with open(pathLabels, "r") as f:
        labels = [line.strip() for line in f.readlines()]

    # load model
    start_time = time.time()
    try:
        maskInterpreter = Interpreter(model_path=maskModel)
        maskInterpreter.allocate_tensors()
        input_details = maskInterpreter.get_input_details()
        output_details = maskInterpreter.get_output_details()
        height = input_details[0]["shape"][1]
        width = input_details[0]["shape"][2]
        floating_model = input_details[0]["dtype"] == np.float32
        input_mean = 127.5
        input_std = 127.5
    except Exception as e:
        returnBadRequest("Error while loading model: " + str(e))
    stop_time = time.time()
    model_load_time = stop_time - start_time

    # preprocess image
    start_time = time.time()
    try:
        nparr = np.frombuffer(event.body, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std
    except Exception as e:
        returnBadRequest("Error while pre-processing image: " + str(e))
    stop_time = time.time()
    preprocess_time = stop_time - start_time

    # predict
    start_time = time.time()
    try:
        maskInterpreter.set_tensor(input_details[0]["index"], input_data)
        maskInterpreter.invoke()
        classes = maskInterpreter.get_tensor(output_details[1]["index"])[0]
        scores = maskInterpreter.get_tensor(output_details[2]["index"])[0]
        min_conf_threshold = 0.7
        masks = []
        for i in range(len(scores)):
            if (scores[i] > min_conf_threshold) and (scores[i] <= 1.0):
                object_name = labels[int(classes[i])]
                masks.append(object_name)

    except Exception as e:
        returnBadRequest("Error while inference: " + str(e))
    stop_time = time.time()
    predict_time = stop_time - start_time

    return {
        "statusCode": 200,
        "body": {
            "model_load_time": model_load_time * 1000,
            "preprocess_time": preprocess_time * 1000,
            "predict_time": predict_time * 1000,
            "masks": masks
        }
    }

def returnBadRequest(msg):
    return {
        "statusCode": 400,
        "body": msg
    }