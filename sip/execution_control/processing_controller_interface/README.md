# SIP Processing Controller Interface

## Roles and Responsibilities

Provides an interface to the SDP functions associated with the scheduling
and execution of Scheduling Block Instances and Processing Blocks on the SDP
system. *It may also eventually provide an interface to give a view of 
Scheduling and Processing Blocks associated with SKA Sub-arrays
(although the current version of this code does not include this feature).*
 
The Consumer of this interface is expected to be the SKA Telescope Manager. 

Exposes the following resources:

- List of Scheduling Block Instances known to SDP.
- Details of a selected Scheduling Block Instances known to SDP.
- List of Processing blocks known to SDP
- Details of a Processing block known to SDP.

The baseline implementation of this is Tango Processing Controller Device 
Server which provides a Processing Controller Device and a set of 
Processing Block Controller Devices. The Processing Controller Device
provides a set of attributes and commands for reasoning about
Scheduling Blocks and the list of Processing Blocks. The Processing Block 
Devices provide drill down capability on individual Processing Blocks.

Processing blocks in SDP can be either be active or queued depending on
the SDP Processing Controller Scheduler (and whether the Processing block is 
real-time or batch). Processing Block devices will be created for all 
Processing Blocks known to SDP irrespective of this state.

A variant with a REST interface based on Flask is also provided. 
