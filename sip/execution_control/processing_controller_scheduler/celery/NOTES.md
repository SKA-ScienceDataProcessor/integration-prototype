# Notes

## Changes

- Remove Scheduling Block events


## Handling of Processing Blocks

### Real-time

These will have a sub-array association as well as a time range.
If resources are available (and they should be given the PCI will check this
when handling the request), they are either queued if the date is in the future
or started immediately.
When started a real-time Processing Block device is started / assigned 
along with the Processing Block which provides a route to monitor and cancel 
the processing. 


### Batch

These have no sub-array association and are scheduled at a point in the future.
The scheduling of batch Processing Blocks is semi-deterministic, based on 
a model and heuristics at the point of allocation, but has a priority and
a degree of scheduling flexibility determined by a priority queue.
When started a batch Processing Block device is started / assigned.


## Scheduler Public functions

### Start event loop

- Start event loop with co-routines for cheap functions and a pool of threads
  for more expensive functions. 
- The event loop needs to be able to watch for a commanded state and act 
  accordingly.
- The event loop needs to be able to watch for Processing Block events
  and act accordingly.
- The event loop should periodically update the database with status 
  information.

## Scheduler Private functions

### Watch and act on processing block events

- Watch for Processing Block events using the configuration db API.
- If new event is found
    - If it is a real-time Processing Block add it to the real-time queue
    - If it is a batch Processing Block

### Watch and act on cancelled processing blocks
### Watch and act on commanded state
### Schedule execution of a processing block
#### Real-time
#### Batch
### Report status of batch Processing Blocks
### Report status of real-time Processing Blocks
### Report status of Processing Blocks
### Report status of Processing Block Controller(s)


## Associated Functions

### Create Processing Block Controller
### Create offline Processing Block Device
### Create real-time Processing Block Device

 
