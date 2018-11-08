FROM skasip/tango_mysql_base
LABEL maintainer="Brian McIlwrath <brian.mcilwrath@stfc.ac.uk> (SKA Project)"

# Use the tangodb baseimage to run a Tango database server
# The base image contains the Ubuntu packages 'mysql-server'
# and 'tango-db' - plus all dependent packages

# MySQL
EXPOSE 3306

# TangoDatabaseds
EXPOSE 10000

# 'tangodb' is based on 'phusion/baseimage' and the following
# commands tie into its 'Run a daemon' scheme
RUN mkdir /etc/service/mysqld
COPY run_mysql.sh /etc/service/mysqld/run
RUN mkdir /etc/service/tango_databaseds
COPY run_tango_databaseds.sh /etc/service/tango_databaseds/run

CMD ["/sbin/my_init"]
