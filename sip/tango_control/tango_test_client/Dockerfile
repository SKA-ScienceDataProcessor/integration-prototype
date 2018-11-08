FROM ubuntu:17.10

WORKDIR /app

# FIXME need to specify (dummy) tango host?
RUN apt-get update && \
    apt-get install -y python3-tango

CMD ["sleep", "3600"]
