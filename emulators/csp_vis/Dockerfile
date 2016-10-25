#
# Build with:
#   > docker build -t send_vis_data:devel
#
# Run with
#   > docker run send_vis_data:devel <json file>
#
FROM ubuntu:16.04
MAINTAINER Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
# Install dependencies
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y python-minimal
RUN apt-get install -y python-pip
RUN apt-get install -y libboost-system-dev
RUN apt-get install -y libboost-python-dev
RUN apt-get install -y libboost-program-options-dev
RUN pip install -U pip setuptools
# Clean up apt cache?
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# TODO(BM) Checkout code from git here instead of copy.
COPY . /app
WORKDIR /app
# Install python requirements
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "send_vis_data.py"]
# TODO(BM) need to be able to pass this json file into the docker container
CMD ["send_vis_data_1.json", "-v"]
