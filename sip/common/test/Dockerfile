FROM ubuntu
MAINTAINER David Terrett
USER root

# Install Python 3 and pip
RUN apt-get -y update && apt-get -y install python3 python3-pip
RUN python3 -m pip install rpyc

# Create non-privileged user
RUN adduser --disabled-password -gecos 'unprivileged user' sdp

# Copy application files
COPY test_task.py /home/sdp/
COPY test_service.py /home/sdp/

# Make the application executable
RUN chmod +x /home/sdp/test_task.py
RUN chmod +x /home/sdp/test_service.py
