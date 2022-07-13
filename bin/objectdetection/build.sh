#!/usr/bin/env bash
ARCH="${1:-amd64}"
image=edgerun/objectdetection
version=$(git rev-parse --short HEAD)

basetag="${image}:${version}"

# change into project root
# BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# PROJECT_ROOT=$(realpath "${BASE}/../../../")
# cd $PROJECT_ROOT
tmp="$(mktemp)"

# scaffold build folder
sed "s/VERSION/$version/g" objectdetection.yml >"${tmp}"
faas-cli build --shrinkwrap -f "${tmp}"
cd ./build/objectdetection || exit

# build container
if [[ "$ARCH" == "amd64" ]]
then
  echo "Build amd64"
  docker build -t ${basetag}-amd64 --build-arg WATCHDOG_VERSION=1.0.0-amd64  .
elif [[ "$ARCH" == "arm32v7" ]]
then
  echo "Build arm32v7"
  docker build -t ${basetag}-arm32v7 --build-arg WATCHDOG_VERSION=1.0.0-arm32v7  .
elif [[ "$ARCH" == "arm64v8" ]]
then
  echo "Build arm64v8"
  docker build -t ${basetag}-arm64v8 --build-arg WATCHDOG_VERSION=1.0.0-arm64v8 .
else
  echo "Unknown arch: $ARCH"
fi

cd ../../
rm "${tmp}"
