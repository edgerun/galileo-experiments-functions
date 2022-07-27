#!/bin/bash
VERSION=${1:-2.1.0}

docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

cd ./docker

docker build -t edgerun/tflite:"${VERSION}"-arm64v8 -f Dockerfile.tflite.arm64v8 .
#docker build -t edgerun/tflite:"${VERSION}"-amd64 -f Dockerfile.tflite.amd64 .
#docker build -t edgerun/tflite:"${VERSION}"-arm32v7 -f Dockerfile.tflite.arm32v7 .
