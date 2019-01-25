FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -U

#RUN addgroup -S sip && adduser -S sip -G sip && addgroup sip root
#USER sip

WORKDIR /home/sip

COPY sip_pbc sip_pbc

ENTRYPOINT ["celery"]
CMD ["-C", "-A", "sip_pbc.tasks", "worker", "--loglevel=INFO"]
