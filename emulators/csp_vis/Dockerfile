#
# Build with:
#   > docker build -t send_vis_data:devel
#
# Run with
#   > docker run send_vis_data:devel <json file>
#

# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/


FROM ubuntu:16.04
MAINTAINER Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
# Install dependencies
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y libboost-system-dev
RUN apt-get install -y libboost-python-dev
RUN apt-get install -y libboost-program-options-dev
RUN pip3 install -U pip setuptools
# Clean up apt cache
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# Copy scripts into container.
COPY . /app
WORKDIR /app
# Install python requirements
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python", "send_vis_data.py"]
# TODO(BM) need to be able to pass this json file into the docker container
CMD ["send_vis_data_1.json", "-v"]
