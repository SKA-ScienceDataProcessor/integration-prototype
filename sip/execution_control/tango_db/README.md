# SIP Tango Database

This folder (and sub-folders) provide the files needed to deploy a Tango 
database. 

## Introduction

This is a first attempt to build and run a Tango database server in a Docker 
container in as close a manner as possible to that used on a 
bare-metal or VirtualBox system.

The Tango database server is a single process called `DataBaseds` but this 
relies on
1. A running MySQL server containing a database with name 'tango' 
   pre-populated with the correct schema.
2. To communicate with the outside world it also relies on the (C++) 
   `libtango9.so` library, other CORBA omniORB libraries, and the C++ 
   runtime etc.


## Building and running the Docker Images

### With docker-compose

To build images:

```bash
docker-compose build
```

To run the `skasip/tango_db` container:

```bash
docker-compose up tango_db
```

### Without docker-compose

1. Build the 'device server base image':
    ```bash
    docker build -t skasip/tango_mysql_base tango_mysql_base/
    ```
    
2. Build the 'Runnable container' from this:
    ```bash
    docker build -t skasip/tango_db tango_db/
    ```
    
3. Run this - either publishing container port 10000 or 
   remapping it in case of an existing device server instance
   running on that port already. 
    ```bash
    docker run -d -p <host port>:10000 skasip/tango_db
    ```
    * Can also publish port 3306 (mysql) if desired
    * -d (or not) to daemonise the 'docker run'








