[![Docker Pulls](https://img.shields.io/docker/pulls/skasip/csp_vis_sender_01.svg)](https://hub.docker.com/r/skasip/csp_vis_sender_01/)
[![Docker Stars](https://img.shields.io/docker/stars/skasip/csp_vis_sender_01.svg)](https://hub.docker.com/r/skasip/csp_vis_sender_01/)
[![](https://images.microbadger.com/badges/version/skasip/csp_vis_sender_01.svg)](https://microbadger.com/images/skasip/csp_vis_sender_01 "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/image/skasip/csp_vis_sender_01.svg)](https://microbadger.com/images/skasip/csp_vis_sender_01 "Get your own image badge on microbadger.com")



# CSP visibility sender, version 1

(from old SIP master branch)

## Description

Emulates the CSP-SDP visibility data interface by sending visibility 
data as SPEAD heaps. Data is sent using one or more UDP streams. The 
items within each SPEAD heap is defined by the 
[ICD documents](https://confluence.ska-sdp.org/pages/viewpage.action?pageId=145653762). 

In the current implementation of this emulator the visibility data
consists of simple patterns within the complex amplitudes. 
It is expected that this will be extended in future iterations of the
SIP to include more realistic data either from simulation or broadcast 
of observed data sets. 

## Running the emulator

The emulator can either by run as a python script or from a Docker container. 

### Running the Python script
`python send_vis_data.py [-v] [-p] myconfig.json`

Where `myconfig.json` is a JSON settings file.

### Using Docker
The Docker image can be built with the following command:

`docker build -t send_vis_data:devel .`

and can be run as follows:

`docker run -v $PWD:/data send_vis_data:devel [-v] [-p] </data/myconfig.json>`

*Note: JSON configurations files are passed to the container by mounting a host
directory as a data volume using the `-v` flag.*

## Configuration

- The emulator is configured using a JSON file.
- The JSON file has three top level groups used to specify the SPEAD protocol
flavour to be used, the global observation settings of visibility data and 
the subset of the observation being sent by the node being configured. 
```JSON
{
    "spead_flavour": {},
    "observation": {},
    "sender_node": {}
}
```
- `spead_flavour` which defines the 'flavour' of the SPEAD heap to sent.
- `observation` defines the observation from which the visibility data 
belongs as well as options for configuring how the data is generated.
- `sender_node` which defines the subset of the observation to send as well 
as the UDP streams (host/ports) to which the data should be sent.

An example of the `spead_flavour` group is as follows and it is unlikely
that any of these options will need to be changed unless interfacing 
with other telescopes. 
```JSON
{
    "spead_flavour": {
      "version": 4,
      "item_pointer_bits": 64,
      "heap_address_bits": 40,
      "bug_compat_mask": 0
    }
}
```
- `version` is the SPEAD protocol version and should be set to `4` 
- `item_pointer_bits` is the number of bits for item pointer fields and
should be set to `64`
- `heap_address_bits` is the number of bits of the heap address space.
 This should be always a multiple of 8 and less than or equal to 
 `item_pointer_bits`. A value of 40 bits allows for heaps of up to 1 TB 
 and up to 2^23 variables.
- `bug_compat_mask` is enumerator in order to support compatibility
 with bugs in previous versions of the PySPEAD library 
 (see [http://spead2.readthedocs.io/en/latest/py-flavour.html]()). The
  value of `0` disables bug compatibility.  


An example of the `observation` group is as follows. **NOTE** The settings 
in this section need to be reviewed and will likely change.
```JSON
{
    "observation": {
      "frequency": {
        "start_hz": 50e6,
        "end_hz": 100e6,
        "num_channels": 50
      },
      "time": {
        "start_time_utc": "2016-09-12 15:35:01.1234",
        "num_times": 5,
        "observation_length_s": 50
      },
      "simulation": {
        "TBD": "needs review"
      }
    }
}
```

An example of the `sender_node` group is as follows:
```JSON
{
  "sender_node": {
    "num_channels": 2,
    "start_channel": 0,
    "streams": [
      {
        "host": "127.0.0.1",
        "port": 8001,
        "threads": 1
      },
      {
        "host": "127.0.0.1",
        "port": 8002,
        "threads": 1
      }
    ]
  }
}
```
- `num_channels` the number of channels to send (subset of total observation)
- `start_channel` the index of the first channel to send
- `streams` list of UDP streams to use in sending `num_channels`. The number
of channels per stream (or heap) is equal to the `num_channels` divided by
the number of `streams` in the list. Streams are described by the following
keys:
  - `host` the host (IP) to send data to
  - `port` the port to send data to
  - `threads` the number of threads used to send the SPEAD heaps

## References
1. [ICD documents](https://confluence.ska-sdp.org/pages/viewpage.action?pageId=145653762)
2. [SPEAD format](https://casper.berkeley.edu/astrobaki/images/9/93/SPEADsignedRelease.pdf)
3. [SPEAD2 library](https://github.com/ska-sa/spead2)

