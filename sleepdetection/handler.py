import numpy as np
import imutils
import time
import dlib
import cv2
from math import hypot

def mid(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

def eye_aspect_ratio(eye_landmark, face_roi_landmark):
    left_point = (face_roi_landmark.part(eye_landmark[0]).x, face_roi_landmark.part(eye_landmark[0]).y)
    right_point = (face_roi_landmark.part(eye_landmark[3]).x, face_roi_landmark.part(eye_landmark[3]).y)

    center_top = mid(face_roi_landmark.part(eye_landmark[1]), face_roi_landmark.part(eye_landmark[2]))
    center_bottom = mid(face_roi_landmark.part(eye_landmark[5]), face_roi_landmark.part(eye_landmark[4]))

    hor_line_length = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_length = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    if ver_line_length == 0:
        return hor_line_length
    ratio = hor_line_length / ver_line_length
    return ratio

def mouth_aspect_ratio(lips_landmark, face_roi_landmark):
    left_point = (face_roi_landmark.part(lips_landmark[0]).x, face_roi_landmark.part(lips_landmark[0]).y)
    right_point = (face_roi_landmark.part(lips_landmark[2]).x, face_roi_landmark.part(lips_landmark[2]).y)

    center_top = (face_roi_landmark.part(lips_landmark[1]).x, face_roi_landmark.part(lips_landmark[1]).y)
    center_bottom = (face_roi_landmark.part(lips_landmark[3]).x, face_roi_landmark.part(lips_landmark[3]).y)

    hor_line_length = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_length = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
    if hor_line_length == 0:
        return ver_line_length
    ratio = ver_line_length / hor_line_length
    return ratio

def handle(event, context):

    modelUrl = "./function/model/68facelandmarks.dat"

    # load model and image
    start_time = time.time()
    try:
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(modelUrl)
    except Exception as e:
        return returnBadRequest("Error while model loading: " + str(e))
    stop_time = time.time()
    model_load_time = stop_time - start_time

    # preprocess
    start_time = time.time()
    try:
        im_arr = np.frombuffer(event.body, dtype=np.uint8)
        frame = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        frame = imutils.resize(frame, width=992)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        return returnBadRequest("Error while pre-processing: " + str(e))
    stop_time = time.time()
    preprocess_time = stop_time - start_time

    # predict
    start_time = time.time()
    try:
        # detect faces in the grayscale frame
        rects = detector(gray, 0)
        faces = []
        for rect in rects:
            faces.append(predictor(gray, rect))
    except Exception as e:
        return returnBadRequest("Error while inference: " + str(e))
    stop_time = time.time()
    predict_time = stop_time - start_time

    # post process
    start_time = time.time()
    try:
        results = []
        for landmark_list in faces:
            left_eye_ratio = eye_aspect_ratio([36, 37, 38, 39, 40, 41], landmark_list)
            right_eye_ratio = eye_aspect_ratio([42, 43, 44, 45, 46, 47], landmark_list)
            eye_open_ratio = (left_eye_ratio + right_eye_ratio) / 2
            inner_lip_ratio = mouth_aspect_ratio([60, 62, 64, 66], landmark_list)
            outter_lip_ratio = mouth_aspect_ratio([48, 51, 54, 57], landmark_list)
            mouth_open_ratio = (inner_lip_ratio + outter_lip_ratio) / 2

            results.append({
                "mouth_open_ratio": mouth_open_ratio,
                "eye_open_ratio": eye_open_ratio
            })

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
            "results": results
        }
    }

def returnBadRequest(msg):
    return {
        "statusCode": 400,
        "body": msg
    }