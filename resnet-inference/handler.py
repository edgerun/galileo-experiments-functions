import base64
import io
import json
import logging
import os
import tempfile
import time

import numpy as np
import tensorflow as tf
from PIL import Image
from minio import Minio, ResponseError
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.python.keras.utils import data_utils

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                    level=logging._nameToLevel[os.environ.get('LOG_LEVEL', 'INFO')],
                    datefmt='%Y-%m-%d %H:%M:%S')

if os.environ['SET_GPU_MEMORY_LIMIT'] == 'true':
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.experimental.set_virtual_device_configuration(
                gpus[0],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=int(os.environ['GPU_MEMORY_LIMIT']))])
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Virtual devices must be set before GPUs have been initialized
            print(e)


def load_model(context, folder: str = None):
    with context.lock:
        try:
            logging.debug(context)
            print(context.model)
        except AttributeError:
            logging.info('loading model...')

            script_dir = os.path.dirname(__file__)
            rel_path = "data/model.h5"
            weights = os.path.join(script_dir, rel_path)

            if os.environ['MODEL_STORAGE'] == 's3':
                if not folder:
                    raise AttributeError('Folder has to be passed if downloading weights from minio')
                file_name = os.path.join(folder, 'resnet_model.h5')
                download_from_minio(
                    bucket_name=os.environ['MODEL_BUCKET'],
                    object_name=os.environ['MODEL_OBJECT_NAME'],
                    local_file_name=file_name
                )
                weights = file_name

                index_file = os.path.join(folder, 'index.json')
                download_from_minio(
                    bucket_name=os.environ['CLASS_INDEX_BUCKET'],
                    object_name=os.environ['CLASS_INDEX_OBJECT_NAME'],
                    local_file_name=index_file
                )
            else:
                rel_path = "data/labels.json"
                index_file = os.path.join(script_dir, rel_path)

            with open(index_file) as fd:
                context.class_index = json.load(fd)

            context.model = ResNet50(weights=weights)


# copied from source: imagenet_utils.py
def decode_predictions(preds, class_index, top=5):
    results = []
    for pred in preds:
        top_indices = pred.argsort()[-top:][::-1]
        result = [tuple(class_index[str(i)]) + (pred[i],) for i in top_indices]
        result.sort(key=lambda x: x[2], reverse=True)
        results.append(result)
    return results


def get_image_from_request(req):
    data = req['picture']
    logging.info('reading image from request')
    img_bytes = io.BytesIO(base64.b64decode(data))
    return img_bytes


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


def create_minio_client():
    return Minio(os.environ['MINIO_URL'],
                 access_key=os.environ['MINIO_ACCESS_KEY'],
                 secret_key=os.environ['MINIO_SECRET_KEY'],
                 secure=False)


def get_image_from_s3(req, folder):
    file_name = os.path.join(folder, 'classify')
    download_from_minio(
        bucket_name=req['bucket_name'],
        object_name=req['object_name'],
        local_file_name=file_name
    )
    return file_name


def load_image(req, folder: str = None):
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


def timer():
    return time.time()


def handle(event, context):
    start = timer()
    tmp_dir = tempfile.TemporaryDirectory()
    req = event.body
    req = json.loads(req)

    load_model_start = timer()
    load_model(context, '/tmp/models')
    load_model_time = timer() - load_model_start

    load_img_start = timer()
    img = load_image(req, tmp_dir.name)
    load_image_time = timer() - load_img_start

    preprocess_start = timer()
    x = preprocess_image(img)
    preprocess_time = timer() - preprocess_start

    pred_start = timer()
    preds = context.model.predict(x)
    pred_end = timer()

    total_time = pred_end - start
    pred_time = pred_end - pred_start
    predictions = decode_predictions(preds, context.class_index, top=3)

    tmp_dir.cleanup()

    out = {
        'total_duration': total_time,
        'load_model_duration': load_model_time,
        'load_image_duration': load_image_time,
        'preprocess_duration': preprocess_time,
        'inference_duration': pred_time,
        'result': {
            'label_id': predictions[0][0][0],
            'label_name': predictions[0][0][1],
            'confidence': float(predictions[0][0][2])
        },
        'start_ts': start,
        'load_model_ts': load_model_start,
        'load_image_ts': load_img_start,
        'preprocess_ts': preprocess_start,
        'pred_ts': pred_start,
        'end_ts': pred_end
    }

    # decode the results into a list of tuples (class, description, probability)
    # (one such list for each sample in the batch)
    logging.debug(f'Predicted: {predictions[0]}')

    return {
        "statusCode": 200,
        "body": json.dumps(out)
    }


def preprocess_image(img):
    img = img.convert('RGB')
    img = img.resize((224, 224), Image.NEAREST)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x
