import base64
import json
import time
import cv2
import numpy as np

def get_image_from_request(req):
    data = req['picture']
    img_bytes = base64.b64decode(data)
    return img_bytes

def handle(event, context):
    BODY_PARTS = {"Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                  "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                  "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                  "LEye": 15, "REar": 16, "LEar": 17, "Background": 18}

    POSE_PAIRS = [["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
                  ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
                  ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
                  ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
                  ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"]]

    protoFile = "./function/model/poseestimation.prototxt"
    weightsFile = "./function/model/poseestimation.caffemodel"
    threshold = 0.05

    # load model
    start_time = time.time()
    try:
        net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
        stop_time = time.time()
    except Exception as e:
        return returnBadRequest("Error while model loading: " + str(e))
    model_load_time = stop_time - start_time

    # preprocess
    start_time = time.time()
    try:
        req = event.body
        req = json.loads(req)
        im_arr = np.frombuffer(get_image_from_request(req), dtype=np.uint8)
        frame = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]
        inWidth = 600
        inHeight = 600
        inp = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),(0, 0, 0), swapRB=False, crop=False)
        net.setInput(inp)
    except Exception as e:
        return returnBadRequest("Error while pre-processing: " + str(e))
    stop_time = time.time()
    preprocess_time = stop_time - start_time

    # predict
    start_time = time.time()
    try:
        out = net.forward()
    except Exception as e:
        return returnBadRequest("Error while inference: " + str(e))
    stop_time = time.time()
    predict_time = stop_time - start_time

    # post process
    start_time = time.time()
    try:
        points = []
        for i in range(len(BODY_PARTS)):
            heatMap = out[0, i, :, :]
            _, conf, _, point = cv2.minMaxLoc(heatMap)
            x = (frameWidth * point[0]) / out.shape[3]
            y = (frameHeight * point[1]) / out.shape[2]
            points.append((int(x), int(y)) if conf > threshold else None)

        filtered_points = []
        for p in points:
            if p != None:
                filtered_points.append(p)

        precision = 0.00
        if len(points) > 0:
            precision = len(filtered_points) / len(points)
    except Exception as e:
        return returnBadRequest("Error while post-processing: " + str(e))
    stop_time = time.time()
    post_process_time = stop_time - start_time

    return {
        "statusCode": 200,
        "body": {
            "model_load_time": model_load_time * 1000,
            "preprocess_time": preprocess_time * 1000,
            "predict_time": predict_time * 1000,
            "post_process_time": post_process_time * 1000,
            "pose_pairs": POSE_PAIRS,
            "points": points,
            "precision": str(precision)
        }
    }

def returnBadRequest(msg):
    return {
        "statusCode": 400,
        "body": msg
    }