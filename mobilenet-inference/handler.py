import base64
import io
import json
import logging
import os
import tempfile
import time

import numpy as np
import tflite_runtime.interpreter as tflite
from PIL import Image
from minio import ResponseError, Minio

EDGETPU_SHARED_LIB = "libedgetpu.so.1"

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                    level=logging._nameToLevel[os.environ.get('LOG_LEVEL', 'INFO')],
                    datefmt='%Y-%m-%d %H:%M:%S')


def load_labels(path):
    with open(path, 'r') as f:
        return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image


def classify_image(interpreter, image, top_k=1):
    """Returns a sorted array of classification results."""
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))

    # If the model is quantized (uint8 data), then dequantize the results
    if output_details['dtype'] == np.uint8:
        scale, zero_point = output_details['quantization']
        output = scale * (output - zero_point)

    ordered = np.argpartition(-output, top_k)
    return [(i, output[i]) for i in ordered[:top_k]]


def make_interpreter(path_model, use_tpu=False):
    if use_tpu:
        logging.info('use edgetpu')
        interpreter = tflite.Interpreter(path_model,
                                         experimental_delegates=[tflite.load_delegate(EDGETPU_SHARED_LIB)])
    else:
        logging.info('use cpu')
        interpreter = tflite.Interpreter(path_model)
    return interpreter


def timer():
    return time.time()


def create_minio_client():
    return Minio(os.environ['MINIO_URL'],
                 access_key=os.environ['MINIO_ACCESS_KEY'],
                 secret_key=os.environ['MINIO_SECRET_KEY'],
                 secure=False)


def download_from_minio(bucket_name, object_name, local_file_name, minio=None):
    if minio is None:
        minio = create_minio_client()
    try:
        logging.debug(
            f'Download object from S3. Bucket: {bucket_name}, Object: {object_name}, Local file name: {local_file_name}')
        minio.fget_object(bucket_name=bucket_name,
                          object_name=object_name,
                          file_path=local_file_name)
    except ResponseError:
        logging.error('Downloading the trained model from S3 failed!')
        raise


def use_tpu():
    return os.environ.get('USE_TPU', 'false') == 'true'


def load_model(context, folder: str = None):
    with context.lock:
        try:
            logging.debug(context)
            print(context.model_file)
        except AttributeError:
            logging.info('loading model...')

            if os.environ['MODEL_STORAGE'] == 's3':
                if not folder:
                    raise AttributeError('Folder has to be passed if downloading weights from minio')
                file_name = os.path.join(folder, 'mobilenet_model.tflite')
                download_from_minio(
                    bucket_name=os.environ['MODEL_BUCKET'],
                    object_name=os.environ['MODEL_OBJECT_NAME'],
                    local_file_name=file_name
                )

                labels = os.path.join(folder, 'labels.txt')
                download_from_minio(
                    bucket_name=os.environ['LABELS_BUCKET'],
                    object_name=os.environ['LABELS_OBJECT_NAME'],
                    local_file_name=labels
                )

            else:
                file_name = os.environ['MODEL_FILE']
                labels = os.environ['LABELS_FILE']

            context.model_file = file_name
            context.labels_file = labels


def get_image_from_s3(req, folder) -> str:
    file_name = os.path.join(folder, 'classify')
    download_from_minio(
        bucket_name=req['bucket_name'],
        object_name=req['object_name'],
        local_file_name=file_name
    )
    return file_name


def load_image(req, folder: str = None) -> Image:
    image_storage = os.environ.get('IMAGE_STORAGE')
    logging.debug(f"Fetch image from: {image_storage}")
    if image_storage is None:
        raise AttributeError('Please specify where to look for image. Supported: request, s3')
    if image_storage == 'request':
        img = get_image_from_request(req)
    elif image_storage == 's3':
        if folder is None:
            raise AttributeError('Folder must be given if downloading image from s3.')
        img = get_image_from_s3(req, folder)
    else:
        raise AttributeError(f'Unknown image storage: {image_storage}. Supported: request, s3')
    return Image.open(img)


def get_image_from_request(req) -> io.BytesIO:
    data = req['picture']
    logging.info('reading image from request')
    img_bytes = io.BytesIO(base64.b64decode(data))
    return img_bytes


def preprocess_image(img: Image, width: int, height: int):
    return img.convert('RGB').resize((width, height), Image.ANTIALIAS)


def handle(event, context):
    start = timer()
    tmp_dir = tempfile.TemporaryDirectory()
    req = event.body
    req = json.loads(req)

    load_model_start = timer()
    load_model(context, '/tmp/models')
    interpreter = make_interpreter(context.model_file, use_tpu())
    interpreter.allocate_tensors()
    _, height, width, _ = interpreter.get_input_details()[0]['shape']
    labels = load_labels(context.labels_file)
    load_model_time = timer() - load_model_start

    load_img_start = timer()
    img = load_image(req, tmp_dir.name)
    load_image_time = timer() - load_img_start

    preprocess_start = timer()
    image = preprocess_image(img, width=width, height=height)
    preprocess_time = timer() - preprocess_start

    pred_start = timer()
    results = classify_image(interpreter, image)
    pred_end = timer()

    total_time = pred_end - start
    pred_time = pred_end - pred_start

    label_id, prob = results[0]

    tmp_dir.cleanup()

    out = {
        'total_duration': total_time,
        'load_model_duration': load_model_time,
        'load_image_duration': load_image_time,
        'preprocess_duration': preprocess_time,
        'inference_duration': pred_time,
        'result': {
            'label_id': int(label_id),
            'label_name': labels[label_id],
            'confidence': prob
        },
        'start_ts': start,
        'load_model_ts': load_model_start,
        'load_image_ts': load_img_start,
        'preprocess_ts': preprocess_start,
        'pred_ts': pred_start,
        'end_ts': pred_end
    }

    logging.debug(f'height: {height}, width: {width}')

    logging.debug(f'Predicted: {labels[label_id]}')

    return {
        "statusCode": 200,
        "body": json.dumps(out)
    }
