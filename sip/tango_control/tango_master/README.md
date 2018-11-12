# SIP SDP Tango Master (SDP Element Master)

See description in the SIP report for more details on this service.

Start using the `docker-compose.yaml` file from the parent tango_control folder.


## Running the SDP Master

For an interactive prompt inside the running container:

```bash
docker exec -it $(docker ps -q -f name=tango_master) /bin/bash
```

To start the MasterController Device server.

```bash
python3 SDPMasterDeviceServer.py 1
```
