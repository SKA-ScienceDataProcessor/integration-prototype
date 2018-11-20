# SIP TANGO client image

Docker image which provides a client for interfacing with to SIP tango 
devices.

Currently this is limited to a few test scripts mounted into the container
and [itango](https://github.com/tango-controls/itango). 

## Using the test client.

```bash
docker exec -it "$(docker ps -q -f name=tango_test_client)" /bin/bash
```

or 

```bash
docker exec -it "$(docker ps -q -f name=tango_test_client)" itango3
```

## Useful commands

### Get list of devices

#### From the iTango prompt:

```python
refreshdb
lsdev
```

#### Using the Python API:

Query the TANGO database for a list of devices served by a server for a 
given device class. See [get_device_name()](http://www.esrf.eu/computing/cs/tango/pytango/v920/database.html#PyTango.Database.get_device_name)

```python
# coding: utf-8
"""Get list of services."""
from tango import Database
db = Database()
db.get_device_name('*', '*')
```
