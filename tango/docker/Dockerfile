# This is the first attempt at a Dockerfile to install the Tango
# libraries, PyTango and (optionally) itango3 on an Ubuntu 17.04 container.

# At the end it tries to connect to a Tango Database in the HOST (this
# assumes the - default- "bridge" network) to list the known device
# servers

# BKMc 20170608 

FROM ubuntu:zesty
MAINTAINER Brian McIlwrath
USER root

ENV  DEBIAN_FRONTEND=noninteractive
# This was the address on the system I developed under - correct as needed!
ENV TANGO=172.17.0.1:10000

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN echo tango-common tango-common/tango-host string $TANGO | debconf-set-selections
#RUN apt-get -y install python3
#RUN apt-get -y install libtango9
#RUN apt-get -y install libtango-dev
#
# Only really need this package as it auto-installs all others!
RUN apt-get -y install python3-pytango
#RUN apt-get -y install python3-itango

COPY list_tango_database.py .
RUN chmod 775 list_tango_database.py
RUN ./list_tango_database.py
