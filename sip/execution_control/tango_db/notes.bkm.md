This is a first attempt to build and run a Tango database server in a Docker 
container in as close a manner as possible to that used on a 
bare-metal or virtualbox system.

The Tango database server is a single process called 'DataBaseds' but this 
relies on
1.  a running Mysql server containing a database with name 'tango' 
    pre-populated with the correct schema.
2. To communicate with the outside world it also relies on the (C++) 
   'libtango9.so' library, other Corba OMNIOrb) libraries and the C++ 
   runtime etc.

To use these files:

1. Build the 'device server base image':
    ```bash
    docker build -t skasip/tango_mysql tango_mysql/
    ```
2. Build the 'Runnable container' from this:
    ```bash
    docker build -t skasip/tango_databaseds tango_databaseds/
    ```
3. Run this - either publishing port container port 10000 or 
   remapping it in case of an existing device server instance 
    ```bash
    docker run -d -p <host port>:10000 skasip/tango_databaseds
    ```
      * Can also expose port 3306 (mysql) if desired
      * -d (or not) to daemonise the 'docker run'





