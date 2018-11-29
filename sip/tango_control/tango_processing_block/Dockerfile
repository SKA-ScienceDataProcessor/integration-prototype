FROM skasip/tango_docker_base:1.1.3
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

USER root

COPY requirements.txt .
RUN pip3 install -r requirements.txt

USER sip

COPY app app

ENTRYPOINT ["./app/processing_block_ds.py"]
CMD ["1", "-v4"]

