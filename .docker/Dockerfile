FROM python:3.9-buster

RUN apt-get update && apt-get install -y libgdal-dev

RUN python -m pip install -U wheel pip

RUN python -m pip install osgeo numpy pandas Cython