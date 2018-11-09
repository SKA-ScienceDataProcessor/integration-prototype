FROM python:3.6-alpine3.6
WORKDIR /app
COPY requirements.txt .
RUN apk update && \
    pip install --no-cache-dir -r requirements.txt
COPY app app
ENV REDIS_HOST redis
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:9095", "app.app:APP"]
