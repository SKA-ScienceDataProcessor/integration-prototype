FROM ubuntu:17.10
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3-tango python3-pip git

# SIP configuration data library
RUN pip3 install -e \
    git+https://github.com/SKA-ScienceDataProcessor/integration-prototype@master#egg=skasip-config-db\&subdirectory=sip/execution_control/configuration_db

RUN useradd -ms /bin/bash sip
USER sip
WORKDIR /home/sip
