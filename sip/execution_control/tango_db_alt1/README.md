# SIP Tango Database

This folder (and sub-folders) provide the files needed to deploy a Tango 
database. This is a test of an alternative deployment method where the database
is in a separate image from the Tango Databaseds device server.

## Quickstart

Build Docker images with:

```bash
docker-compose build
```

Create containers with

```bash
docker-compose up
```

Tear town with
```bash
docker-compose rm -f -s
```
