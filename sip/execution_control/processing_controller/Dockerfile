FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

COPY requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -r /root/.cache

RUN addgroup -S sip && adduser -S sip -G sip
USER sip
WORKDIR /home/sip

COPY scheduler scheduler
COPY processing_block_controller processing_block_controller

# Docker daemon automatically monitors the PID1 process in the container.
# if a better health check can be defined, add it here
# HEALTHCHECK ...

ENTRYPOINT ["python"]
CMD ["-u", "-m", "scheduler"]
