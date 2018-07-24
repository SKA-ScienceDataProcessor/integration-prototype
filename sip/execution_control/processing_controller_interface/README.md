# SIP Processing Controller Interface (PCI)

## Introduction

This component provides an (external) interface to SDP for scheduling
the execution of Scheduling Block Instances (SBI). SBIs represent the 
executable unit of scheduling of observation on the telescope. Each SBI is 
expected to contain one or more Processing Blocks (PB), which provide a 
description of the SDP processing required. 

This interface is presented as three main resources:

- The list of SBIs known to SDP. This resource provides the ability
  to query, cancel and register additional SBIs with the SDP system.

- The list of PBs known to SDP. This is essentially provides a flattened 
  view of the processing currently running or requested to be run by SDP as 
  PBs are expected to be the primary unit of scheduling of resources in the 
  SDP system. This resource provides the ability to query and cancel PBs.

- A Subarray centric view on the SDPs SBIs and PBs. This provides a 
  view into the system indexed by the subarray which SBIs and PBs are 
  associated. As subarrays are active for a given time, this interface will
  either expose SBIs and PBs for the current active subarrays (and not expose
  batch processing tasks for subarrays which are not longer active) or 
  provide the ability to index SDP by Subarray at a given time. This resource
  (or set of commonly themed resources) provide the ability to query,
  cancel and register SBIs against a given Subarray.  

The Consumer of this interface is expected to be the SKA Telescope Manager.

The primary implementation of this interface is a set of Tango devices 
identifying as the Processing Controller Device and a set 16 SDP Subarray
devices. An alternative RESTful (Flask based) web services implementation
is also being developed alongside the baseline version for additional 
experimentation.


For more details on the design and implementation of this component see the
SDP Conflunence page:

<https://confluence.ska-sdp.org/display/WBS/SIP%3A+%5BEC%5D+Processing+Controller+Interface+Service>

## Implementation folders:

- `tango`: A set Tango device server and set of Tango devices presenting 
   attributes and commands exposing the resources described above. 

- `flask_api`: A RESTful (JSON), Flask based web services API exposing a set 
   of HTTP endpoints for the PCI resources described above.
   
- `flask_ui`: A simple frontend web UI to the `flask_api` interface.
