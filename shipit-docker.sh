#!/bin/sh

set -ex

if [ x$CI_DOCKER_TAG == x ]
then
    # Non-CI build
    CI_DOCKER_TAG=latest
fi

echo "### Building base container"

BASE=dotscience-python-base:$CI_DOCKER_TAG

docker build -t $BASE -f Dockerfile.base .

echo "### Generating the dotscience-python3 docker image"

sed s/CI_DOCKER_TAG/$CI_DOCKER_TAG/ < Dockerfile.python > Dockerfile.python.tmp
docker build -t dotscience-python3:$CI_DOCKER_TAG -f Dockerfile.python.tmp .

if [ -n "${CI_DOCKER_PYTHON_IMAGE}" ]
then
    echo "Pushing to ${CI_DOCKER_PYTHON_IMAGE}"
    docker tag dotscience-python3:$CI_DOCKER_TAG ${CI_DOCKER_PYTHON_IMAGE}
    docker push ${CI_DOCKER_PYTHON_IMAGE}
fi
