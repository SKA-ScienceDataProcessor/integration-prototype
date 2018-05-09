# Flask Processing Controller Frontend UI AP

## Roles and responsibilities

This service is provides a frontend web UI for interacting with the
the RESTful API Flask Processing Controller Interface service.   


## Quickstart

First start the Flask RESTful API provided by the Flask variant of the
Processing Controller Interface service found in the `flask_api` folder. 

Then start the Flask web app in this folder as follows.

```bash
export FLASK_APP=app/app.py
export FLASK_DEBUG=True
flask run --host=0.0.0.0 --port=5001
```

This exposes a Flask web application on the URL `http://localhost:5001/`.
