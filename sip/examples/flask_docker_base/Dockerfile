FROM python:3.7.1-alpine3.7

COPY requirements.txt .
RUN apk update && \
    apk add --no-cache curl && \
    apk add --no-cache git && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    find /usr/local/lib/python3.7/ -name 'tests' -exec rm -r '{}' +

RUN addgroup -S sip && adduser -H -S sip -G sip
WORKDIR /sip
USER sip

