#### CSP visibility data (SPEAD) emulator  

**TODO(BM) convert to rst for use with sphinx**

This is a python script that can be used to send very simple fake SPEAD data 
packets with the aim of emulating the CSP visibility data interface. 

##### Direct running

`python send_vis_data.py [-v] <json config file>`


##### Use with docker

Build with:

`docker build -t send_vis_data:devel .`

Run with:

`docker run send_vis_data:devel <json config file>`

##### References
1. https://confluence.ska-sdp.org/pages/viewpage.action?pageId=145653762
2. https://github.com/ska-sa/spead2
