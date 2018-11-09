FROM python:3.6-alpine3.6

WORKDIR /app

COPY requirements.txt .
RUN apk update && \
    pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -r /root/.cache

COPY scheduler app
COPY mock_processing_block_controller mock_processing_block_controller

# Docker daemon automatically monitors the PID1 process in the container.
# if a better health check can be defined, add it here
# HEALTHCHECK ...

ENTRYPOINT ["python", "-u", "-m", "scheduler"]
