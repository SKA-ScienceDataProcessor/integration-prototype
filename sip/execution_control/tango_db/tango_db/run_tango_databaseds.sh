#!/bin/sh

exec su - tango -s /bin/sh -c "/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000"
