FROM skasip/tango_docker_base:1.1.3
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

USER root
COPY requirements.txt .
RUN pip3 install -r requirements.txt

USER sip
RUN mkdir ~/.ipython

COPY *.py ./

ENV TANGO_HOST=localhost:10000

ENTRYPOINT ["itango3"]
