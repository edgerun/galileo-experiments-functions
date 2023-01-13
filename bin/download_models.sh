#!/usr/bin/env bash
cd ./poseestimation
mkdir model
cd ..
cd ./sleepdetection
mkdir model
cd ..
cd ./objectdetection
mkdir model
cd ..
cd ./gundetection
mkdir model
cd ..
cd ./maskdetection
mkdir model
cd ..
cd ./mobilenet-inference
mkdir data
cd ..
cd ./resnet-inference
mkdir data
cd ..
cd ./efficientnet-inference
mkdir data
cd ..

#download model for poseestimation
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=149EikDB4v38tIFRBj0eznq5u1FPjFBEe' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=149EikDB4v38tIFRBj0eznq5u1FPjFBEe" -O ./poseestimation/model/poseestimation.caffemodel && rm -rf /tmp/cookies.txt
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=1xVEDxkHJlaN_R3S3Y3N6y7ux3f-tS5Uu' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1xVEDxkHJlaN_R3S3Y3N6y7ux3f-tS5Uu" -O ./poseestimation/model/poseestimation.prototxt && rm -rf /tmp/cookies.txt

#download model for sleepdetection
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=1mpA0H53frYFm7QCFxMsaRxaEPmpEkSvW' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1mpA0H53frYFm7QCFxMsaRxaEPmpEkSvW" -O ./sleepdetection/model/sleepdetection.dat && rm -rf /tmp/cookies.txt

#download model for maskdetection
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=1EJk3kfn548mpjIt2wEqNvujG3ZwQbAGm' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1EJk3kfn548mpjIt2wEqNvujG3ZwQbAGm" -O ./maskdetection/model/maskdetection.tflite && rm -rf /tmp/cookies.txt
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=1pjNV1eKYzq3ZRrm0hcUD-LMx3o92tCW8' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1pjNV1eKYzq3ZRrm0hcUD-LMx3o92tCW8" -O ./maskdetection/model/maskdetection.txt && rm -rf /tmp/cookies.txt


#download model for gundetection
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=13PoX1xCl4z7Fe2KfUwS4MtmhcBPXHBLJ' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=13PoX1xCl4z7Fe2KfUwS4MtmhcBPXHBLJ" -O ./gundetection/model/gundetection.xml && rm -rf /tmp/cookies.txt

#download model for objectdetection
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=1a4gTfJOoMZHFy9WOhslmGs9saowOau4X' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1a4gTfJOoMZHFy9WOhslmGs9saowOau4X" -O ./objectdetection/model/objectdetection.tflite && rm -rf /tmp/cookies.txt

#download mobilenet
wget https://raw.githubusercontent.com/google-coral/edgetpu/master/test_data/mobilenet_v2_1.0_224_quant_edgetpu.tflite -O ./mobilenet-inference/data/model.edgetpu.tflite
wget https://raw.githubusercontent.com/google-coral/edgetpu/master/test_data/mobilenet_v2_1.0_224_quant.tflite -O ./mobilenet-inference/data/model.tflite
wget https://raw.githubusercontent.com/google-coral/edgetpu/master/test_data/imagenet_labels.txt -O ./mobilenet-inference/data/labels.txt

#download model for resnet-inference
wget https://github.com/keras-team/keras-applications/releases/download/resnet/resnet50_weights_tf_dim_ordering_tf_kernels.h5 -O ./resnet-inference/data/model.h5
wget https://storage.googleapis.com/download.tensorflow.org/data/imagenet_class_index.json -O ./resnet-inference/data/labels.json

#download model for efficientnet-inference
#wget https://github.com/leondgarse/keras_efficientnet_v2/releases/download/effnetv2_pretrained/efficientnetv2-b0-imagenet.h5 -O ./efficientnet-inference/data/model.h5
wget https://github.com/leondgarse/keras_efficientnet_v2/releases/download/effnetv1_pretrained/efficientnetv1-b0-imagenet.h5 -O ./efficientnet-inference/data/model.h5
wget https://storage.googleapis.com/download.tensorflow.org/data/imagenet_class_index.json -O ./efficientnet-inference/data/labels.json