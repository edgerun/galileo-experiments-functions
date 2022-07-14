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
wget https://drive.google.com/file/d/149EikDB4v38tIFRBj0eznq5u1FPjFBEe/view?usp=sharing -O ./poseestimation/model/poseestimation.caffemodel
wget https://drive.google.com/file/d/1xVEDxkHJlaN_R3S3Y3N6y7ux3f-tS5Uu/view?usp=sharing -O ./poseestimation/model/poseestimation.prototxt

#download model for sleepdetection
wget https://drive.google.com/file/d/1mpA0H53frYFm7QCFxMsaRxaEPmpEkSvW/view?usp=sharing -O ./sleepdetection/model/sleepdetection.dat

#download model for maskdetection
wget https://drive.google.com/file/d/1EJk3kfn548mpjIt2wEqNvujG3ZwQbAGm/view?usp=sharing -O ./maskdetection/model/maskdetection.tflite
wget https://drive.google.com/file/d/1pjNV1eKYzq3ZRrm0hcUD-LMx3o92tCW8/view?usp=sharing -O ./maskdetection/model/maskdetection.txt

#download model for gundetection
wget https://drive.google.com/file/d/1EJk3kfn548mpjIt2wEqNvujG3ZwQbAGm/view?usp=sharing -O ./gundetection/model/gundetection.xml

#download model for objectdetection
wget https://drive.google.com/file/d/1aJZeq2o5U-rAGC2p-0I3hpSahfmyS2nX/view?usp=sharing -O ./objectdetection/model/objectdetection.tflite
wget https://drive.google.com/file/d/1nUoym9zaXOTez83ZQy0OzqJoAxCtNtde/view?usp=sharing -O ./objectdetection/model/objectdetection.xml

