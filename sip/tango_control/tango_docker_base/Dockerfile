FROM ubuntu:17.10
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3-tango python3-pip git

RUN pip3 install -U skasip-config-db skasip-logging

RUN useradd -ms /bin/bash sip
USER sip
WORKDIR /home/sip
