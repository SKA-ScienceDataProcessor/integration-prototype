# Dockerfile for building a container that runs the skeleton slave controller
#
# Because it needs to copy files from outside this directory you have to
# run docker build from the SIP repository root.
#
# docker build -f sip/slave/Dockerfile -t slave_controller .

FROM ubuntu
MAINTAINER David Terrett
USER root

# Install Python 3 and pip
RUN apt-get -y update && apt-get -y install python3 python3-pip
RUN python3 -m pip install zmq
RUN python3 -m pip install rpyc
RUN python3 -m pip install simplejson

# Create non-privileged user
RUN adduser --disabled-password -gecos 'unprivileged user' sdp

# Copy application files
COPY sip/ /home/sdp/integration-prototype/sip/
WORKDIR /home/sdp/integration-prototype
