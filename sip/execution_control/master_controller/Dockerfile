FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup -S sip && adduser -S sip -G sip
USER sip
WORKDIR /home/sip

COPY app app

HEALTHCHECK --interval=15s --timeout=2s --start-period=5s --retries=2 \
    CMD python3 -m app.health

ENTRYPOINT ["python3", "-m", "app"]
CMD []
