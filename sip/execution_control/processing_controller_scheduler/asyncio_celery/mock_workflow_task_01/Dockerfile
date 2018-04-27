FROM python:3.6.4-alpine3.7
LABEL maintainer="Benjamin Mort <ben.mort@gmail.com>"

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY task.py .

ENTRYPOINT ["python3", "task.py"]
CMD []
