#!/bin/sh

set -ex

if [ x$CI_DOCKER_TAG = x ]
then
    # Non-CI build
    CI_DOCKER_TAG=latest
fi

echo "### Building base container"

BASE=dotscience-python-test:$CI_DOCKER_TAG

docker build -t $BASE -f Dockerfile.test .

docker run -v dotscience-python-test-examples:/dsbuild/.hypothesis/examples $BASE /bin/bash -c "cd dsbuild ; pytest dotscience"
