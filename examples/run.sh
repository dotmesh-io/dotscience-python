#!/bin/bash -e
if [ ! -f env ]; then
    echo "please copy env.sample to env and fill it in"
    exit 1
fi
rm -rf model
. ./env
PYTHONPATH=..:$PYTHONPATH python3 train.py
