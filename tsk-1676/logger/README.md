Tango devices can log to one or more of the following using the
syntax "device::instance" for the logging target

* The console ("console" - instance can be omitted)
* A file ("file::<filename>)
* Any other suitably configured device server ("device::<full device name>")

This example shows a simple device server to log messages

Note that logging to a server JUST means that the Device Server has a
suitable 'log' method - so this could be added to ANY Server


This directory should be the home for files related to the 'top-level'
SDP module logger (as in the diagram at 
https://drive.google.com/file/d/0B7gp_PBvQlOLM09udDhlUlBORGc)


