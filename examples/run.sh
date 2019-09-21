#!/bin/bash -xe
if [ ! -f env ]; then
    echo "please copy env.sample to env and fill it in"
    exit 1
fi
. ./env
env
PYTHONPATH=..:$PYTHONPATH python3 train.py
