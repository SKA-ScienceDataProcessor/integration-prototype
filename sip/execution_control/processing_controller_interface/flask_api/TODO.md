# TODO

## Configuration Database 

### Client: Bugs

- [ ] the function `get_processing_block_ids()` raises a type error
      if no Processing Blocks are registered in the db. A temporary fix the
      has been made to the local copy of the client in this service.
- [ ] `get_block_details` fail for processing blocks where
      when there are duplicate processing block ids
      in such a case the number of returned block details > the number
      of block_ids passed to the function. See `processing_block_list.py` 
      ~line 23. This may be a 'feature' but if so adding processing 
      blocks with duplicate ids needs to trigger an exception in the add 
      SBI method. 

### Client: Suggestions / comments for review

- [x] Add function to drop / clear the db
- [ ] Rename `set_scheduling_block` to 
      `add_scheduling_block`?
- [ ] Seed additional fields into the db 
      on adding a scheduling block instance?
      client `set_scheduling_block()` method
- [ ] Consider having non-generator version of `get_block_details()`
      for cases where only one block is required. This could be written as a
      wrapper on the generator.
- [ ] Consider renaming argument of `get_block_details` from `block_id`
      to `block_ids` to hint that this needs to be a list
- [ ] Add (debug) logging using python logging for key events / actions
      in the client?
- [ ] Method to get Scheduling Block Instance id for given Processing Block id?
- [ ] Added client function `get_sub_array_scheduling_block_ids()`
      which returns list of SBI Id's for a given sub-array.
- [ ] Review how many connections are made to the db when loading the client
      module multiple times and instantiating a client object for each of these.
      If this is too many (> few) we might be better off making the DB 
      connection a module variable.
      
### Schema: suggestions / comments for review

- [ ] Add version to SBI schema
- [ ] Rename of `sched_block_instance_id` to `id` as this is the primary key
      for the data Scheduling Block Instance data items and this better 
      matches the what is being done for Processing Blocks which also use
      `id` as their primary key.
- [ ] Reviewing key names used to build the data store hierarchy. At the moment
      there seems to be redundancy in items such as 'project' being part of the
      the SBI id as well as the PB id. Also consider shortening inserted
      label keys. ie. 
        'scheduling_block' -> 'sbi' and 
        'processing_block' -> 'pb'  


## FLask API

- [ ] Review routes in light of Tango Device
      discussion
- [ ] Fix naming of Blueprints & docstrings for sloppy use of Scheduling Block
      vs Scheduling Block Instance
- [ ] Add logging

### Tests

- [ ] Check PB / SBI delete methods.
- [ ] TODO or review scope of testing in current version of SIP

