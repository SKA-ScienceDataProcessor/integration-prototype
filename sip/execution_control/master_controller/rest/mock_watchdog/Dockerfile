FROM python:3.6-alpine3.6
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

WORKDIR /app

COPY requirements.txt .
RUN apk update && \
    pip install --no-cache-dir -r requirements.txt
ENV TZ=-1

COPY app app

ENTRYPOINT ["python3", "-m", "app"]
