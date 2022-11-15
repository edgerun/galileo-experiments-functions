#!/usr/bin/env bash
ARCH="${1:-amd64}"

image=resi5/resnet-inference
version=$(git rev-parse --short HEAD)
tf2_version=2.7.0
basetag="${image}:${version}"

docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

export DOCKER_BUILD_KIT=1
export DOCKER_CLI_EXPERIMENTAL=enabled

tmp="$(mktemp)"

# scaffold build folder
sed "s/VERSION/$version/g" resnet-inference.yml >"${tmp}"
# download models
#sh bin/download_models.sh
faas-cli build --shrinkwrap -f "${tmp}"
cd ./build/resnet-inference || exit

# build container
if [[ "$ARCH" == "amd64" ]]
then
  echo "Build amd64"
  docker build -t ${basetag}-amd64 --build-arg WATCHDOG_VERSION=1.0.0-amd64 --build-arg TF2_VERSION=${tf2_version} .
elif [[ "$ARCH" == "arm64v8" ]]
then
  echo "Build arm64v8"
  docker build -t ${basetag}-arm64v8 --platform linux/arm64 --build-arg WATCHDOG_VERSION=1.0.0-arm64v8 --build-arg TF2_VERSION=${tf2_version} .
else
  echo "Unknown arch: $ARCH"
fi

cd ../../
rm "${tmp}"

