FROM python:3.6-alpine3.6
WORKDIR /app
COPY requirements.txt .
RUN apk update && \
    pip install --no-cache-dir -r requirements.txt
COPY demo.py .
ENTRYPOINT ["python3", "demo.py"]
