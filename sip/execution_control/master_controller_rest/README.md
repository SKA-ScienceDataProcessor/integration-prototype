[![Docker Pulls](https://img.shields.io/docker/pulls/skasip/master_controller_rest.svg)](https://hub.docker.com/r/skasip/master_controller_rest/)
[![Docker Stars](https://img.shields.io/docker/stars/skasip/master_controller_rest.svg)](https://hub.docker.com/r/skasip/master_controller_rest/)
[![](https://images.microbadger.com/badges/version/skasip/master_controller_rest.svg)](https://microbadger.com/images/skasip/master_controller_rest "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/image/skasip/master_controller_rest.svg)](https://microbadger.com/images/skasip/master_controller_rest "Get your own image badge on microbadger.com")

# SIP Master Controller Service (REST variant)

## Roles and responsibilities

The Master Controller performs the following roles:

* Provides an interface to query SDP state(s).
* Provides a list of SDP endpoints.
* (Ensures SDP services are kept running as much as possible without operator 
  intervention.) 
* (Provides a limited set of commands for control of SDP services.)


## Quick start

### Starting the Master Controller

Start the Master Controller in production mode:

```bash
docker-compose up -d
```

Start the Master Controller in development mode:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Development mode exposes additional ports to localhost.


### Clean up the Master Controller

```bash
docker-compose rm -s -f
```

### Running the unit tests

(First start the Master Controller in development mode)

```bash
python3 -m unittest tests/test.py
```

## References

1. [SIP Master Controller design](https://confluence.ska-sdp.org/display/WBS/SIP%3A+%5BEC%5D+Master+Controller+Service)
1. [SDP System-Level Module Decomposition View (§2.1.1.1)](https://docs.google.com/document/d/1M0S20FWn4Dsb8nl9duIoW93OEiXlzVDGh8sqImOl6S0)
1. [SDP System-Level C&C View (§2.1)](https://docs.google.com/document/d/1FTGfuy1R4_xjEug5ENPZwXqfAEy9ydqYXCXP__48KKw)
1. [SKA Control System Guidlines (000-000000-010 Rev 01)](https://ska-aw.bentley.com/SKAProd/Search/QuickLink.aspx?n=000-000000-010&t=3&d=Main%5ceB_PROD&sc=Global&r=01&i=view)
1. [SKA Tango Developers Guideline (000-000000-011 Rev 01](https://docs.google.com/document/d/1vr6xcYTpYOZnECmu47KG5cdyKMF9zE089ufBT5CprNY/edit#heading=h.gjdgxs)
1. [SDP_TM_LOW_ICD 100-000000-029_03](https://docs.google.com/document/d/13E9bgygFz5H-fPrRXSgwxQWTrGNk_yCLCE35NeLhNRs)
1. [SDP_TM_MID_ICD 300-000000-029_03](https://docs.google.com/document/d/1HI8efEahniLJZUfhZoDclump9L-SkEkD_m7kIJBgkcE)
