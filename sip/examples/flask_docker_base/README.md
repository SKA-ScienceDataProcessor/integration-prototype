# Example SIP Flask Docker base image

<https://hub.docker.com/r/skasip/tc_flask_base>

## Introduction

Example Docker base image for developing SIP Flask applications.

This is intended to provide a common Docker base image for developing RESTful JSON alternatives, written using Flask, to the Tango Control components which provide the external control and monitoring interface to SDP.

This image is currently only used by the example Processing Block interface controller, `sip/examples/flask_processing_controller`.

This image creates a `sip` user and sets the working directory to `/sip`.

## Getting started

Build the image (note the image can also be found at <https://hub.docker.com>):

```bash
docker build -t skasip/tc_flask_base
```

Test (interactively) with:

```bash
docker run --rm -it --entrypoint=/bin/bash skasip/tc_flask_base
```

Example usage:

```Dockerfile
FROM skasip/tc_flask_base
# Copy flask app, eg:
# COPY app /sip/app
EXPOSE 5000
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app:APP"]
```
