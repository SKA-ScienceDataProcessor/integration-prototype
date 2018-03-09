# Processing Controller Interface (REST variant)

## Roles and responsibilities

Provides an interface to the Processing Controller which supports the following
activities:

1. Submit a new Scheduling Block
2. Query list of Scheduling Blocks
3. Query details of a Scheduling Block
4. Query list of Processing Blocks
5. Query details of a Processing Block

The Processing Controller is the SDP master scheduler of all Processing blocks
currently registered with the SDP system. 

## Quickstart

```bash
docker-compose build
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

or 

```bash
docker stack deploy -c docker-compose.dev.yml [stack name]
```


```bash
docker-compose rm -s -f
```

```bash
docker stack rm [stack name]
```

```bash
export FLASK_APP=app/app.py
export FLASK_DEBUG=True
flask run
```
