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
#download model for poseestimation
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=149EikDB4v38tIFRBj0eznq5u1FPjFBEe' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=149EikDB4v38tIFRBj0eznq5u1FPjFBEe" -O ./poseestimation/model/poseestimation.caffemodel && rm -rf /tmp/cookies.txt
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1xVEDxkHJlaN_R3S3Y3N6y7ux3f-tS5Uu" -O ./poseestimation/model/poseestimation.prototxt

#download model for sleepdetection
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1mpA0H53frYFm7QCFxMsaRxaEPmpEkSvW" -O ./sleepdetection/model/sleepdetection.dat

#download model for maskdetection
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1EJk3kfn548mpjIt2wEqNvujG3ZwQbAGm" -O ./maskdetection/model/maskdetection.tflite
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1pjNV1eKYzq3ZRrm0hcUD-LMx3o92tCW8" -O ./maskdetection/model/maskdetection.txt


#download model for gundetection
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=13PoX1xCl4z7Fe2KfUwS4MtmhcBPXHBLJ" -O ./gundetection/model/gundetection.xml

#download model for objectdetection
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1a4gTfJOoMZHFy9WOhslmGs9saowOau4X" -O ./objectdetection/model/objectdetection.tflite