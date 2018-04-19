FROM python:3.6-alpine3.6
LABEL maintainer="David Terrett <david.terrett@stfc.ac.uk>"

WORKDIR /app

COPY requirements.txt .
RUN apk update && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    apk add --no-cache curl && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -r /root/.cache

COPY app app

EXPOSE 5000

ENTRYPOINT ["python3", -m "app"]
