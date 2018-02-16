# SIP Processing Block Controller

## Roles and Responsibilities

- Execution of Processing Blocks.
    - The default assumption is one Processing Block per Processing Block 
      Controller (although depending on the implementation this may not be a 
      hard requirement).
    - Interacts with various Platform Services and SDP Services to complete the
      end-to-end execution of each Processing Block which it is responsible 
      for.
    - *Note that assignment of Processing Blocks to instances of this service 
      is the responsibility of the Processing Controller (Scheduler)*    
    - *Note that a Processing Block is defined by a set of workflow stages, 
       where a workflow stage might be (but is not limited to):*
       - *Preparation and staging of input data, including buffer, model and 
         configuration data.*
       - *A parallel processing pipeline or workflow that makes use of an 
          Execution Engine.*
       - *Cleaning up and preparation of output data products*
- Provides information on the state of the execution of the Processing Block(s) 
  it is responsible for. This information is made available to the Processing 
  Controller (Interface and Scheduler).
