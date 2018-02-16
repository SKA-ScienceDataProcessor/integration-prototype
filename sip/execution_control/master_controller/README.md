# SIP Master Controller

## Roles and Responsibilities

The Master Controller performs the following roles:

- Provides an interface to query SDP state(s).
- Provides a set of commands to control the state of SDP. (The state of SDP 
  determines how SDP will behave with respect to the execution of Processing 
  Blocks.)
- Provides a list of SDP endpoints (for service discovery by other SKA
  elements).

Additional roles that ***might*** be assigned to the Master Controller and 
are under consideration:
- Ensuring Services are kept running in a healthy state without intervention
  of a human operator.
- Provides a limited set of commands for control of SDP services.

## Implementation variants

This currently has two implementation variants:

- **Tango**: the baseline SDP Master Controller implementation which exposes 
a Tango interface to the SKA Telescope Manager.
- **REST**: a JSON REST interface mirroring the Tango version, implemented 
using Flask.
