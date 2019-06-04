FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

COPY Pipfile* ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

RUN addgroup -S sip && adduser -S sip -G sip
USER sip
WORKDIR /home/sip

COPY task.py .
COPY _version.py .

ENTRYPOINT ["python3", "task.py"]
CMD [ "{\"duration\": 20}" ]
