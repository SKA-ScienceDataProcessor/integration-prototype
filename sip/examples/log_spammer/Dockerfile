FROM python:3.6.2-alpine3.6
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

RUN pip install skasip-logging==1.0.11

RUN addgroup -S sip && adduser -S sip -G sip
USER sip
WORKDIR /home/sip

COPY _version.py /home/sip
COPY log_spammer.py /home/sip

ENTRYPOINT ["python3", "log_spammer.py"]
CMD ["0.1"]
