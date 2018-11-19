FROM python:3.6-alpine3.6
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

WORKDIR /app

COPY requirements.txt .
RUN apk update && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk add --no-cache curl && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -r /root/.cache

COPY app app

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=2s --start-period=5s --retries=2 \
    CMD curl -f http://localhost:5000/ || exit 1

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app.app:APP"]