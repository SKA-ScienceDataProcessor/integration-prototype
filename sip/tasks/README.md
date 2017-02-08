This directory contains the task scripts to be started by 
'docker_slave'. It is included in a docker container as a volume
in 'sip_master/configure.py', and any changes in its name should be reflected in
'_start_docker_slave' function.

It contains currently only one script, 'task.py' .
