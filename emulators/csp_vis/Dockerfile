#
# Build with:
#   > docker build -t send_vis_data:devel
#
# Run with
#   > docker run -v $PWD:/data send_vis_data:devel /data/config.json
#

# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/


FROM ubuntu:16.04
MAINTAINER Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>

# Install dependencies and clean cache
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    libboost-system-dev \
    libboost-python-dev \
    libboost-program-options-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy scripts into container.
COPY . /app
WORKDIR /app

# Install python requirements
RUN pip3 install -U pip setuptools
RUN pip3 install -r requirements.txt

# Command to run
ENTRYPOINT ["python3", "send_vis_data.py"]
CMD ["send_vis_data_1.json", "-v"]
