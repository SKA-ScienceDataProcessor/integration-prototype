FROM mysql:5.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

ENV MYSQL_DATABASE=tango_db
ENV MYSQL_USER=tango
ENV MYSQL_PASSWORD=tango

EXPOSE 3306

# Copy SQL Scripts to /scripts/ directory.
COPY scripts/create_db_tables.sql \
     scripts/stored_procedures.sql \
     /scripts/

# Copy Scripts to
COPY scripts/01_print_env.sh \
     scripts/02_create_db.sql \
     /docker-entrypoint-initdb.d/

CMD ["mysqld", "--sql_mode="]
