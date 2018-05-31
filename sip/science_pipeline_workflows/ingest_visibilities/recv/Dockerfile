FROM python:3.6.4-alpine3.7
COPY --from=skasip/spead_base:latest /root/.cache /root/.cache
COPY requirements.txt .
RUN apk update && \
    apk add --no-cache \
        libstdc++ \
        boost-system \
        boost-program_options && \
    pip3 install -U pip && \
    pip3 install -r requirements.txt && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -rf /root/.cache

WORKDIR /app
COPY async_recv.py /app
# COPY config_schema.json /app

ENTRYPOINT ["python3", "async_recv.py"]
CMD []
