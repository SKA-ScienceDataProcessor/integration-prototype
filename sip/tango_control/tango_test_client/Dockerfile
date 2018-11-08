FROM ubuntu:17.10

WORKDIR /app

# COPY device_server.py /app
# COPY register_device.py /app
COPY requirements.txt /app/requirements.txt


# FIXME need to specify (dummy) tango host?
RUN apt-get update && \
    apt-get install -y python3-tango && \
    apt-get install -y python3-pip git

RUN pip3 install -U -r requirements.txt


CMD ["sleep", "3600"]
