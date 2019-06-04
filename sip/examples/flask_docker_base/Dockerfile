FROM python:3.6.7-alpine3.7

COPY Pipfile* ./
RUN apk update && \
    apk add --no-cache curl && \
    apk add --no-cache git && \
    pip install --no-cache-dir pipenv && \
    pip install --no-cache-dir gunicorn && \
    pipenv install --system --deploy && \
    find /usr/local/lib/python3.7/ -name 'tests' -exec rm -r '{}' +

RUN addgroup -S sip && adduser -H -S sip -G sip
WORKDIR /sip
USER sip

