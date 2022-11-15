#!/bin/bash
VERSION=${1:-2.7.0}
basetag=resi5/tf2:${VERSION}
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

cd ./docker

docker build -t ${basetag}-arm64v8 -f Dockerfile.tf2.arm64v8 .
docker build -t ${basetag}-amd64 -f Dockerfile.tf2.amd64 .


# # push em all
docker push ${basetag}-amd64 &
docker push ${basetag}-arm64v8

wait

docker manifest create -a ${basetag} \
  --amend ${basetag}-amd64 \
  --amend ${basetag}-arm64v8

docker manifest annotate ${basetag} ${basetag}-arm64v8 --os "linux" --arch "arm64" --variant "v8"

docker manifest push --purge ${basetag}
