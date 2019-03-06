#
# Docker Image: skasip/workflow_demo_client
#
# This Dockerfile creates a Docker Image used to provide a terminal prompt
# with all dependencies installed required for:
#   - registering workflows with the SIP Execution Control
#   - Creating a client connection to the SIP Tango Control devices
#
# This avoids having to install Tango and SIP dependencies locally on the
# system running the demo.
#
# Build instructions:
#
#  docker build -t skasip/workflow_demo_client:latest  .
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

COPY workflow ./workflow
COPY generate_sbi_config.py ./

ENTRYPOINT ["/bin/bash"]
