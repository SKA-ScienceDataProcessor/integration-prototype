# Experimental SIP Dockerfile
# ---------------------------
#
# Build the SIP docker image with:
#
#   $ docker build -t sip:test -f sip/Dockerfile .
#
# Run from the top level SIP repository directory.
#

FROM python:3.6-alpine3.6
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

COPY requirements.txt /app/requirements.txt

# Note that libstdc++ is installed as a separate step as this is needed for 
# pyzmq and should not be deleted when removing build dependencies.
RUN apk add --no-cache --virtual build-dependencies \
    g++ gfortran musl-dev python3-dev && \
    apk add --no-cache libstdc++ && \
    pip install -r /app/requirements.txt && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -r /root/.cache && \
    apk del build-dependencies

#HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=3 \
#    CMD curl -f http://localhost:5000/ || exit 1

COPY sip /app/sip
WORKDIR /app

ENTRYPOINT ["python3"]
CMD ["-m", "sip.master"]
