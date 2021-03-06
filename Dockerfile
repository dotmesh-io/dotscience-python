FROM python:3.7

RUN apt-get update && apt-get install git
RUN mkdir dsbuild
COPY .git ./dsbuild/.git
COPY .gitattributes ./dsbuild
COPY dotscience ./dsbuild/dotscience
COPY setup.py ./dsbuild
COPY README.md ./dsbuild
COPY LICENSE ./dsbuild
COPY setup.cfg ./dsbuild
COPY MANIFEST.in ./dsbuild
COPY requirements-docker.txt ./dsbuild

RUN cd dsbuild ; python setup.py install; pip3 install --upgrade pip && pip3 install -r requirements-docker.txt
