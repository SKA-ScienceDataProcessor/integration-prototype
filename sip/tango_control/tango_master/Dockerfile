FROM skasip/tango_docker_base:1.0.6
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

USER root
RUN pip3 install pytest

USER sip

COPY app app
COPY scripts scripts

ENTRYPOINT ["./app/sdp_master_ds.py"]
CMD ["1", "-v4"]
