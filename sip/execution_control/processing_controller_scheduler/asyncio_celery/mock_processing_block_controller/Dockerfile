FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

RUN pip install --no-cache-dir -U "celery[redis]"

WORKDIR /app
COPY *.py mock_processing_block_controller/

ENTRYPOINT ["celery", "-C", "-A", "mock_processing_block_controller.tasks", \
            "worker", "--loglevel=info"]
