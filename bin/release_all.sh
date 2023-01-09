#!/usr/bin/env bash
REPOSITORY="${1:-edgerun}"
VERSION="${2:-$(git rev-parse --short HEAD)}"

sh ./bin/gundetection/release.sh $REPOSITORY $VERSION
sh ./bin/humandetection/release.sh $REPOSITORY $VERSION
sh ./bin/maskdetection/release.sh $REPOSITORY $VERSION
sh ./bin/mobilenet-inference/release.sh $REPOSITORY $VERSION
sh ./bin/objectdetection/release.sh $REPOSITORY $VERSION
sh ./bin/poseestimation/release.sh $REPOSITORY $VERSION
sh ./bin/sleepdetection/release.sh $REPOSITORY $VERSION