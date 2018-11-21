FROM skasip/tango_docker_base:1.1.2
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

COPY app app

ENTRYPOINT ["./app/processing_block_ds.py"]
CMD ["1", "-v4"]

