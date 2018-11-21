FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -U

# FIXME(BMo) Can't run in user space as need access to docker socket! :-(
# RUN addgroup -S sip && adduser -S sip -G sip
# USER sip

WORKDIR /home/sip

COPY *.py processing_block_controller/

ENTRYPOINT ["celery"]
CMD ["-C", "-A", "processing_block_controller.tasks", \
     "worker", "--loglevel=INFO"]
