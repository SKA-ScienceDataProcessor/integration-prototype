FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

COPY app Pipfile* /app/

WORKDIR /app


RUN apk update && \
    apk add --no-cache curl && \
    pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy && \
    rm -r /root/.cache

RUN addgroup -S sip && adduser -S sip -G sip
USER sip
WORKDIR /home/sip


EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=2s --start-period=5s --retries=2 \
    CMD curl -f http://localhost:5000/ || exit 1

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app.app:APP"]
