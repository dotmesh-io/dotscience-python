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

echo "### Shipping package to PyPi"

if [ -n "$PYPI_REPO" ]
then
    REPO_ARG="--repository-url $PYPI_REPO"
fi

docker run $BASE /bin/bash -c "pip install twine ; cd dsbuild ; python3 setup.py sdist bdist_wheel ; twine upload -u $PYPI_USER -p $PYPI_PASSWORD $REPO_ARG dist/*"
