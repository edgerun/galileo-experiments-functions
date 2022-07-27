import base64
import io
import json
import time
import cv2
import numpy as np
cascadeUrl = "./function/model/gundetection.xml"

#based on https://www.geeksforgeeks.org/gun-detection-using-python-opencv/

def get_image_from_request(req):
    data = req['picture']
    img_bytes = base64.b64decode(data)
    return img_bytes

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation = inter)
    return resized

def handle(event, context):
    # load model
    start_time = time.time()
    try:
        gun_cascade = cv2.CascadeClassifier(cascadeUrl)
    except Exception as e:
        return returnBadRequest("Error while model loading: " + str(e))
    stop_time = time.time()
    model_load_time = stop_time - start_time

    # preprocess
    start_time = time.time()
    try:
        req = event.body
        req = json.loads(req)
        nparr = np.fromstring(get_image_from_request(req), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        image = image_resize(image, width=500)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
        stop_time = time.time()
    except Exception as e:
        return returnBadRequest("Error while pre-processing: " + str(e))
    preprocess_time = stop_time - start_time

    # predict
    start_time = time.time()
    try:
        gun = gun_cascade.detectMultiScale(gray, 1.3, 5, minSize = (100, 100))
        gun_exist = False
        if len(gun) > 0:
            gun_exist = True
        stop_time = time.time()
    except Exception as e:
        return returnBadRequest("Error while inference: " + str(e))
    predict_time = stop_time - start_time

    return {
        "statusCode": 200,
        "body": {
            "model_load_time": model_load_time * 1000,
            "preprocess_time": preprocess_time * 1000,
            "predict_time": predict_time * 1000,
            "gunExist": gun_exist
        }
    }

def returnBadRequest(msg):
    return {
        "statusCode": 400,
        "body": msg
    }