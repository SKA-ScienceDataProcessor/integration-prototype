FROM python:3.6.2-alpine3.6
WORKDIR /app
RUN pip install skasip-logging

COPY log_spammer.py /app/log_spammer.py
ENTRYPOINT ["python3", "log_spammer.py"]
CMD ["0.1"]
