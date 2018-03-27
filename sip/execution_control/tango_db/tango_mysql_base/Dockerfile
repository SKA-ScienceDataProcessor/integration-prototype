FROM phusion/baseimage

LABEL maintainer="Brian McIlwrath <brian.mcilwrath@stfc.ac.uk> (SKA Project)"

# Build a container with mysql and tango-db

# Using this as a base image should make it easy to
# run a Tango database Docker container

# Use Ubuntu 17.10 repositories
COPY sources.list /etc/apt/
COPY trusted.gpg /etc/apt
COPY ubuntu-keyring-2012-archive.gpg /etc/apt/trusted.gpg.d/

ENV DEBIAN_FRONTEND=noninteractive

# Set mysql root password
COPY mysql_root_password .
RUN mv /usr/sbin/policy-rc.d .
RUN apt-get update && \
    debconf-set-selections mysql_root_password && \
    apt-get install -y mysql-server

# mysqld fails without this
RUN mkdir /var/run/mysqld && \
    chown mysql:mysql /var/run/mysqld

RUN su - mysql -s /bin/sh -c "/usr/sbin/mysqld&" && \
    apt-get install -y tango-db
RUN mv policy-rc.d /usr/sbin

# Clean up build container
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
