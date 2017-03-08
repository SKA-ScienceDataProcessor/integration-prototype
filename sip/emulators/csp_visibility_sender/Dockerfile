# Build the image with:
#   > cd emulators/csp_visibility_sender
#   > docker build -t csp_visibility_sender .
#
# Create the container with:
#   > docker run -v $PWD:/data -p <port>:<port>/udp csp_visibility_sender /data/config.json
#
# Rerun the container with:
#   > docker start ...
#
#
# http://stackoverflow.com/questions/27596409/how-do-i-expose-a-udp-port-on-docker
#
#
FROM ubuntu:16.04
MAINTAINER Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>

# Install dependencies and clean cache
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libboost-system-dev \
    libboost-python-dev \
    libboost-program-options-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy scripts into container.
COPY . /app/emulators/csp_visibility_sender
COPY ../__init__.py /app/emulators
WORKDIR /app

# Install python requirements
RUN pip3 install -U pip setuptools
RUN pip3 install -r emulators/csp_visibility_sender/requirements.txt

# Command to run
ENTRYPOINT ["python3", "-m", "emulators.csp_visibility_sender"]
CMD ["etc/config.json", "-v"]
