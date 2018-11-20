FROM skasip/tango_docker_base:1.1.2
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

USER root
RUN pip3 install itango

USER sip
RUN mkdir ~/.ipython

COPY *.py ./

ENV TANGO_HOST=localhost:10000

ENTRYPOINT ["itango3"]
