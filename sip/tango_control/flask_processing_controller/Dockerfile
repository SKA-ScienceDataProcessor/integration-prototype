FROM skasip/tc_flask_base:latest

COPY app/api /sip/app/api
COPY app/old.db /sip/app/db
COPY app/app.py /sip/app/app.py
COPY app/__init__.py /sip/app/__init__.py

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=2s --start-period=5s --retries=2 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app.app:APP"]
