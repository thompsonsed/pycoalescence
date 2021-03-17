FROM python:3.9-buster

RUN apt-get update && \
    apt-get install -y libgdal-dev \
    libproj-dev \
    gdal-bin

RUN python3 -m pip install -U wheel pip

RUN python3 -m pip install numpy pandas Cython matplotlib scipy

RUN python3 -m pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version`    
