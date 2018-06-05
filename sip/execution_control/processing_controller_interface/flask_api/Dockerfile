FROM python:3.6.4-alpine3.7

WORKDIR /pci

COPY requirements.txt .
RUN apk update && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    apk add --no-cache curl && \
    find /usr/local/lib/python3.6/ -name 'tests' -exec rm -r '{}' + && \
    rm -r /root/.cache

COPY app/api /pci/app/api
COPY app/db /pci/app/db
COPY app/app.py /pci/app/app.py
COPY app/__init__.py /pci/app/__init__.py

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=2s --start-period=5s --retries=2 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

ENV FLASK_APP app/app.py
ENV FLASK_DEBUG True
ENV SIP_PCI_LOG_LEVEL DEBUG
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=5000"]

# ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app.app:APP"]

