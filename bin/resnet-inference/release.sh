#!/usr/bin/env bash
REPOSITORY="${1:-resi5}"
VERSION="${2:-$(git rev-parse --short HEAD)}"

image=$REPOSITORY/resnet-inference
version=$VERSION
tf2_version=2.7.0
basetag="${image}:${version}"

docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

export DOCKER_BUILD_KIT=1
export DOCKER_CLI_EXPERIMENTAL=enabled

tmp="$(mktemp)"

# scaffold build folder
sed "s/VERSION/$version/g" resnet-inference.yml >"${tmp}"
faas-cli build --shrinkwrap -f "${tmp}"
cd ./build/resnet-inference || exit

# build container
echo "Build amd64"
docker build -t ${basetag}-amd64 --build-arg WATCHDOG_VERSION=1.0.0-amd64  --build-arg TF2_VERSION=${tf2_version} .

echo "Build arm64v8"
docker build -t ${basetag}-arm64v8 --platform linux/arm64 --build-arg WATCHDOG_VERSION=1.0.0-arm64v8 --build-arg TF2_VERSION=${tf2_version} .

cd ../../
rm "${tmp}"


# push em all
docker push ${basetag}-amd64 &
docker push ${basetag}-arm64v8

wait

export DOCKER_CLI_EXPERIMENTAL=enabled

# create the manifest
docker manifest create -a ${basetag} \
  --amend ${basetag}-amd64 \
  --amend ${basetag}-arm64v8

# explicit annotations
docker manifest annotate ${basetag} ${basetag}-arm64v8 --os "linux" --arch "arm64" --variant "v8"

# ship it
docker manifest push --purge ${basetag}
