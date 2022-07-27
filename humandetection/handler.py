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
    # load model
    start_time = time.time()
    try:
        HOGCV = cv2.HOGDescriptor()
        HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    except Exception as e:
        return returnBadRequest("Error while loading model: " + str(e))
    stop_time = time.time()
    model_load_time = stop_time - start_time

    # preprocess image
    start_time = time.time()
    try:
        req = event.body
        req = json.loads(req)
        im_arr = np.frombuffer(get_image_from_request(req), dtype=np.uint8)
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        new_width = 900
        dsize = (new_width, img.shape[0])
        img = cv2.resize(img, dsize, interpolation=cv2.INTER_AREA)
        if img is None:
            return returnBadRequest("Error no image found")
    except Exception as e:
        return returnBadRequest("Error while pre-processing image: " + str(e))
    stop_time = time.time()
    preprocess_time = stop_time - start_time

    # predict
    start_time = time.time()
    found = False
    try:
        bounding_box_cordinates, weights = HOGCV.detectMultiScale(img)
        if any(x > 0.4 for x in weights):
            found = True
    except Exception as e:
        return returnBadRequest("Error while inference: " + str(e))
    stop_time = time.time()
    predict_time = stop_time - start_time

    return {
        "statusCode": 200,
        "body": {
            "predict_time": predict_time * 1000,
            "preprocess_time": preprocess_time * 1000,
            "model_load_time": model_load_time * 1000,
            "found": found
        }
    }

def returnBadRequest(msg):
    return {
        "statusCode": 400,
        "body": msg
    }