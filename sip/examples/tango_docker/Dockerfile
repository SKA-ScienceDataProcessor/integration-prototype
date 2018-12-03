## https://vsupalov.com/docker-env-vars/

FROM ubuntu:17.10

#ARG TANGOHOST=tangodb:9999
ARG TANGO_HOST
ENV TANGO_HOST=${TANGO_HOST}

RUN echo "tango-common tango-common/tango-host string ${TANGO_HOST}" \
    | debconf-set-selections && \
    apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-pytango \
        python3-itango \
        && \
    pip3 install PyTango



