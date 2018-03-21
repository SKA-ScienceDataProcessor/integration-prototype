This is a first attempt to build and run a Tango database server in a Docker 
container in as close a manner as possible to that used on a 
bare-metal or virtualbox system.

The Tango database server is a single process called 'DataBaseds' but this 
relies on
a)  a running Mysql server containing a database with name 'tango' 
    pre-populated with the correct schema.
b) To communicate with the outside world it also relies on the (C++) 
   'libtango9.so' library, other Corba OMNIOrb) libraries and the C++ 
   runtime etc.

To use these files:

1) Build the 'device server baseimage':

    docker build -t skasip/tangodb tangodb_mysql/

2) Build the 'Runnable container' from this:

    docker build -t skasip/tango_host databaseds/

3) Run this - either publishing port 10000 or remapping
   it in case of an existing device server instance 

 docker run -d -p 20000:10000 tango-db-run

  a) Can also expose port 3306 (mysql) if desired

  b) -d (or not) to daemonise the 'docker run'





