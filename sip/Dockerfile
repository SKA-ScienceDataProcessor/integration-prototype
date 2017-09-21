# Experimental SIP Dockerfile
# ---------------------------
#
# Build the SIP docker image with:
#
#   $ docker build -t sip:test -f sip/Dockerfile .
#
# Run from the top level repository directory.
#
# TODO: g++ gfortran musl-dev python3-dev only needed for numpy?
#

FROM python:3.6-alpine3.6
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

# https://github.com/mhart/alpine-node/issues/47
COPY requirements.txt /app/requirements.txt
RUN apk add --no-cache --virtual .build-deps \
    g++ gfortran musl-dev python3-dev && \
    pip install -r /app/requirements.txt && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -r /root/.cache && \
    apk del .build-deps

#HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=3 \
#    CMD curl -f http://localhost:5000/ || exit 1

COPY sip /app/sip
WORKDIR /app

ENTRYPOINT ["python3"]
CMD ["-m", "sip.master"]
