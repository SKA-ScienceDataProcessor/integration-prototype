FROM python:3.6-alpine3.6
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

WORKDIR /app

COPY requirements.txt .
COPY config_db.zip .
RUN apk update && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir config_db.zip

COPY app app

ENTRYPOINT ["python3", "-m", "app"]
