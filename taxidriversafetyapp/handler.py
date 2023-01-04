import base64
import json
import os
import concurrent.futures
import time

import requests
gateway_hostname = os.getenv("API_GATEWAY", "gateway.openfaas")
base_url = "http://" + gateway_hostname + ":8080/function/"

def get_image_from_request(req):
    data = req['picture']
    img_bytes = base64.b64decode(data)
    return img_bytes

def call_request(req, f):
    try:
        r = requests.get(base_url + f, data=req)
        if r.status_code != 200:
            returnBadRequest('Looks like something went wrong while requesting ' + f);
        else:
            return {
                "statusCode": r.status_code,
                "body": r.json()
            }
    except Exception as e:
        return returnBadRequest('Looks like something went wrong: ' + str(e))



def handle(event, context):

    # 1. call human detector
    # 2. if no human found
    # 2.1 return true (driver is safe)
    # 3. if human found
    # 3.1 call mask detection
    # 3.2 call gun detection
    # 4. return wear a mask && no weapon detected

    start_time = time.time()
    req = event.body
    req = json.loads(req)
    if not req['picture']:
        return returnBadRequest("Error: No image.")
    # 1. call human detector
    r = call_request(event.body, "humandetection")
    if r['statusCode'] != 200:
        return r
    results = []

    try:
    # 2. no human found
        if not r['body']['found']:
            isSave = True
        # 3. human found
        else:
        # 3.1 Call mask detection
        # 3.2 Call gun detection
            urls = ["gundetection", "maskdetection"]
            isSave = True
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_to_url = {executor.submit(call_request, event.body, url) for url in urls}
                for future in concurrent.futures.as_completed(future_to_url):
                    try:
                        data = future.result()
                        if data['statusCode'] != 200:
                            return data
                        results.append(data)
                        if 'masks' in data['body']:
                            if "bare" in data['body']['masks']:
                                isSave = False
                        if 'gunExist' in data['body']:
                            isSave = not data['body']['gunExist']

                    except Exception as e:
                        return returnBadRequest('Looks like something went wrong: ' + str(e))

    except Exception as e:
        return returnBadRequest('Looks like something went wrong: ' + str(e) + ' ' + str(r))
    stop_time = time.time()

    return {
        "statusCode": 200,
        "body": {
            "results": results,
            "total_duration": (stop_time - start_time) * 1000,
            "isSave": isSave
        }
    }

def returnBadRequest(msg):
    return {
        "statusCode": 400,
        "body": msg
    }