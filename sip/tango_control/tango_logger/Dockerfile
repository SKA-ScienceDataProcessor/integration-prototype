FROM skasip/tango_docker_base:1.1.3
LABEL maintainer="Brian McIlwrath <brian.mcilwrath@stfc.ac.uk>"

USER root

COPY requirements.txt .
RUN pip3 install -r requirements.txt

USER sip

COPY app app

ENTRYPOINT ["./app/sdp_logger_ds.py"]
CMD ["1", "-v4"]
