FROM python:3.6-alpine3.6
MAINTAINER Nijin Thykkathu

WORKDIR /app

COPY requirements.txt .
RUN apk update && \
    pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -r /root/.cache

COPY app app


ENTRYPOINT ["python", "-u", "-m", "app"]
