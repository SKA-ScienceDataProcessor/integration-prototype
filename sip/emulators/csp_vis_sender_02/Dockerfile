FROM python:3.6.4-alpine3.6 as python-base
COPY requirements.txt .
RUN apk update && \
    apk add --no-cache \
        gcc \
        g++ \
        boost-dev && \
    pip install -r requirements.txt

FROM python:3.6.4-alpine3.6
COPY --from=python-base /root/.cache /root/.cache
COPY --from=python-base requirements.txt .
RUN apk update && \
    apk add --no-cache \
        libstdc++ \
        boost-system \
        boost-program_options && \
    pip install -r requirements.txt && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -rf /root/.cache

WORKDIR /app

COPY app /app/csp_visibility_sender

ENTRYPOINT ["python3", "-m", "csp_visibility_sender"]
CMD []
