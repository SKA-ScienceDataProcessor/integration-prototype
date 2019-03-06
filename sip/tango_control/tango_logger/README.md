# SIP SDP Tango Logger (SDP Element Logger)

See description in the SIP report for more details on this service.

The SDP logger SHOULD be a log aggregator for ALL SDP Tango Devuice Servers. The  file 'tango_logging_notes.txt'
explains some problems in getting this to work as we would wish - and the Tango authors may need to be consoluted!

A descoped JIRA ticket (TSK-2727) was created which defines recipt of logging messages from the SDP Tango Master
Device

To test this

Bring up the 'sip' Docker stack from the file 'tango_logger/docker_compose.yml'

Send the tango_master any command (eg. 'status')

d=DeviceProxy('sip_sdp/elt/master')
d.status()

From a terminal window obtain docker logs of 'logger process'

docker ps |grep logger -> capture ID
docker logs <id>


Should obtain

2019-02-26 15:38:36,607 - sip.tc.sdp_logger - INFO - sdp_logger_device.py:56 |
TANGO Log message - 2019-02-26 15:38:36 - INFO sip_sdp/elt/master Test of Tango logging from 'tc_tango_master'

