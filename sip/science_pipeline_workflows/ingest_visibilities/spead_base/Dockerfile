FROM python:3.6-alpine3.7
COPY requirements.txt .
RUN apk update && \
    apk add --no-cache \
        gcc \
        g++ \
        boost-dev && \
    pip3 install -U pip && \
    pip3 install -r requirements.txt
