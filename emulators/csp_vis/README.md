## CSP visibility data (SPEAD) emulator  

**TODO(BM) convert to rst for use with sphinx**

This is a python script that can be used to send very simple fake SPEAD data 
packets with the aim of emulating the CSP visibility data interface. 

### Running the emulator

The emulator can either by run directly or from a Docker container. 

#### Running directly
`python send_vis_data.py [-v] [-p] myconfig.json`

Where `myconfig.json` is a JSON settings file.

#### Using Docker

The Docker image can be built with the following command:

`docker build -t send_vis_data:devel .`

The docker image can then be run as follows:

`docker run -v $PWD:/data send_vis_data:devel [-v] [-p] </data/myconfig.json>`

*Note: JSON configurations files are passed to the container by mounting a host
directory as a data volume using the `-v` flag.*

### Emulator configuration

TODO(BM)


##### References
1. https://confluence.ska-sdp.org/pages/viewpage.action?pageId=145653762
2. https://github.com/ska-sa/spead2
3. https://docs.docker.com/engine/tutorials/dockervolumes/
