FROM skasip/tango_docker_base:1.0.1
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

USER root
RUN pip3 install itango

USER sip
RUN mkdir ~/.ipython

#ENTRYPOINT ["itango3"]
CMD ["sleep", "36000"]
