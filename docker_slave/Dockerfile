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

# Create non-privileged user
RUN adduser --disabled-password -gecos 'unprivileged user' sdp

# Copy application files
COPY lib /home/sdp/lib
COPY lib/python/ /home/sdp/lib/python/
COPY docker_slave/docker_slave.py /home/sdp/

# Make the application executable
RUN chmod +x /home/sdp/docker_slave.py

# Define entry point. We use CMD rather than ENTRYPOINT because we need to
# have Python running as PID 0 so that it gets the SIGTERM that "docker stop"
# sends.
CMD ["/home/sdp/docker_slave.py"]
