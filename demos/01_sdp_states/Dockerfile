#
# Docker Image: skasip/states_demo_client
#
# This Dockerfile creates a Docker Image used to provide an iTango prompt
# for the startup and states demo.
#
# This avoids having to install Tango and SIP dependencies locally on the
# system running the demo.
#
# Build instructions:
#
#  docker build -t skasip/states_demo_client:latest  .
#
#
FROM skasip/tango_docker_base:1.1.3
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

USER root
RUN pip3 install \
    itango==0.1.6 \
    skasip-config-db==1.2.2 \
    skasip-logging==1.0.14

USER sip
RUN mkdir ~/.ipython
ENV TANGO_HOST=localhost:10000

ENTRYPOINT ["itango3"]
