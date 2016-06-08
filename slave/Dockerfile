# Dockerfile for building a container that runs the skeleton slave controller
#
# Because it needs to copy files from outside this directory you have to
# run docker build from the directory above where this file is stored.
#
# docker build -f docker_slave/Dockerfile -t slave_controller .

FROM ubuntu
MAINTAINER David Terrett
USER root

# Install Python 3 and pip
RUN apt-get -y update && apt-get -y install python3 python3-pip
RUN python3 -m pip install zmq

# Create non-privileged user
RUN adduser --disabled-password -gecos 'unprivileged user' sdp

# Copy application files
COPY common/sip_common/ /home/sdp/integration-prototype/common/sip_common/
COPY components/ /home/sdp/integration-prototype/components/
COPY slave/bin/ /home/sdp/integration-prototype/slave/bin/

# Make the application executable
RUN chmod +x /home/sdp/integration-prototype/slave/bin/slave
