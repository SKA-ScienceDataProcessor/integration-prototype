FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -U "celery[redis]"
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py processing_block_controller/
# COPY /utils/step_one/*.py processing_block_controller/

ENTRYPOINT ["celery", "-C", \
            "-A", "processing_block_controller.tasks", \
            "worker", "--loglevel=info"]
