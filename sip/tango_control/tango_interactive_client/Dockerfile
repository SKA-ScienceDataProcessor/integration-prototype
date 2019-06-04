FROM skasip/tango_docker_base:1.1.3
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

USER root
COPY Pipfile* ./
RUN pip3 install --no-cache-dir pipenv && \
    pipenv install --system --deploy

USER sip
RUN mkdir ~/.ipython

COPY *.py ./

ENV TANGO_HOST=localhost:10000

ENTRYPOINT ["itango3"]
