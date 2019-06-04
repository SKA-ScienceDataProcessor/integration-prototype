FROM ubuntu:18.04
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3-pytango python3-pip && \
    pip install --no-cache-dir pipenv

COPY Pipfile* ./
RUN pipenv install --system --deploy

RUN useradd -ms /bin/bash sip
USER sip
WORKDIR /home/sip
