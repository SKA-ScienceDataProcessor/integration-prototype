FROM ubuntu:17.10

WORKDIR /app

# COPY device_server.py /app
# COPY register_device.py /app

# FIXME need to specify (dummy) tango host?
RUN apt-get update && \
    apt-get install -y python3-tango

CMD ["sleep", "3600"]
