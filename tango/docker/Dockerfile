# This is the first attempt at a Dockerfile to install the Tango
# libraries, PyTango and (optionally) itango3 on an Ubuntu 17.04 container.

# May need some work stil!

FROM ubuntu:17.04
MAINTAINER Brian McIlwrath
USER root

ENV  DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install python3
RUN apt-get -y install libtango9
RUN apt-get -y install libtango-dev
RUN apt-get -y install python3-pytango
#RUN apt-get -y install python3-itango

ENV  DEBIAN_FRONTEND teletype 



