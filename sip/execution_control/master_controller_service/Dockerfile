FROM python:3.6-alpine3.6
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

WORKDIR /app

COPY requirements.txt .
RUN apk update && \
    apk add --no-cache git && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir git+https://github.com/SKA-ScienceDataProcessor/integration-prototype#egg=config_db\&subdirectory=sip/execution_control/configuration_db/redis && \
    apk del git 

COPY app app

ENTRYPOINT ["python3", "-m", "app"]
