FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install dask distributed

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
