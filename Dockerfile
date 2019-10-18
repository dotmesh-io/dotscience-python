FROM python:3.8

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

RUN cd dsbuild ; python3 setup.py install
#RUN rm -rf dsbuild
