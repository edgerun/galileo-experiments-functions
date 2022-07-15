#!/bin/bash
VERSION=${1:-2.1.0}

cd ./docker

docker build -t pruellerpaul/opencv:"${VERSION}"-arm64v8 -f Dockerfile.opencv.arm64v8 .
docker build -t pruellerpaul/opencv:"${VERSION}"-amd64 -f Dockerfile.opencv.amd64 .
docker build -t pruellerpaul/opencv:"${VERSION}"-arm32v7 -f Dockerfile.opencv.arm32v7 .
