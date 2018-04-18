# TANGO Control System Dockerfile
FROM centos:7

COPY resources/maxiv.repo /etc/yum.repos.d/
COPY resources/wait-for-it.sh /usr/local/bin/

RUN yum -y install epel-release \
    && yum -y install supervisor zeromq \
    && yum-config-manager --save \
        --setopt=epel.includepkgs="zeromq libsodium openpgm" \
    && yum -y install \
        libtango9 \
        tango-common \
        tango-db

ENV ORB_PORT=10000
ENV TANGO_HOST=127.0.0.1:${ORB_PORT}

EXPOSE ${ORB_PORT}

CMD /usr/local/bin/wait-for-it.sh ${MYSQL_HOST} --timeout=60 --strict \
    -- /usr/bin/DataBaseds 2 -ORBendPoint giop:tcp::10000
