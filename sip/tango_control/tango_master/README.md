# SIP SDP Tango Master (SDP Element Master)

See description in the SIP report for more details on this service.


## Quick-start


Start using the `docker-compose.yaml` file from the parent `tango_control`
folder.

```bash
docker stack deploy -c docker-compose.yml tagno
```

Get an interactive prompt inside the running container:

```bash
docker exec -it -w /home/sip/tango_master $(docker ps -q -f name=tango_master) /bin/bash
```

This can also be done by using the script found in the `tango_control` folder:

```bash
./get_interactive_prompt.sh
```

and select option '3'.


Register the SDP Master device (`sip_sdp/elt/master`) and start the 
Device server (`sdp_master_ds/1`):

```bash
python3 register_device.py
python3 sdp_master_ds.py 1 -v4
```
