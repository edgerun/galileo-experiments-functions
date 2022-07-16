#!/bin/bash
VERSION=${1:-2.1.0}
basetag=edgerun/opencv:${VERSION}
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

cd ./docker

docker build -t ${basetag}-arm64v8 -f Dockerfile.opencv.arm64v8 .
docker build -t ${basetag}-amd64 -f Dockerfile.opencv.amd64 .
docker build -t ${basetag}-arm32v7 -f Dockerfile.opencv.arm32v7 .


# # push em all
docker push ${basetag}-amd64 &
docker push ${basetag}-arm64v8 &
docker push ${basetag}-arm32v7

wait

docker manifest create ${basetag} \
  --amend ${basetag}-amd64 \
  --amend ${basetag}-arm32v7 \
  --amend ${basetag}-arm64v8

docker manifest annotate ${basetag} ${basetag}-arm64v8 --os "linux" --arch "arm64" --variant "v8"
docker manifest annotate ${basetag} ${basetag}-arm32v7 --os "linux" --arch "arm" --variant "v7"

docker manifest push --purge ${basetag}
