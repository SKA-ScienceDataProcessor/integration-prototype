## SIP Processing Controller Scheduler

## Roles and Responsibilities

This component provides a service which schedules Processing Blocks for
execution.

This requires the following functions:

- Registration of Processing Blocks into the scheduler
- Removal of Processing Blocks from the scheduler (including termination of 
  processing if required).
- Retrieval of information on Processing Blocks.
- Prioritisation of execution of Processing Blocks
- Evaluation of resource availability for running Processing Blocks
- Provisioning of available resources for running Processing Blocks
- Initialising the execution of a Processing Block (which is run using 
  a Processing Block Controller) 
