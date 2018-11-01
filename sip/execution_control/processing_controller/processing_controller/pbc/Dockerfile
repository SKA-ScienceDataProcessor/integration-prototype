FROM python:3.6.4-alpine3.7
LABEL maintainer="Nijin Thykkathu <nijin.thykkathu@stfc.ac.uk>"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /utils/workflow_stage_scripts/*.py processing_block_controller/
