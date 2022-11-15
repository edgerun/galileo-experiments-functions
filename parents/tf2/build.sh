#!/bin/bash
VERSION=${1:-2.7.0}

docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

cd ./docker

docker build -t resi5/tf2:"${VERSION}"-arm64v8 -f Dockerfile.tf2.arm64v8 .
docker build -t resi5/tf2:"${VERSION}"-amd64 -f Dockerfile.tf2.amd64 .
