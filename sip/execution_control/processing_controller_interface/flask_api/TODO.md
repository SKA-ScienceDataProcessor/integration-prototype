# TODO

## Configuration Database Client

### Bugs
- [ ] The Generator returned from `get_block_details(<block_id>)` method
      iterates over all blocks even those not associated with the `block_id`
      argument.

### Improvements
- [ ] Add version to SBI schema
- [ ] Convert database client to functions
      (instead of a class)
- [x] Add function to drop / clear the db
- [ ] Rename `set_scheduling_block` to 
      `add_scheduling_block`?
- [ ] Seed additional fields into the db 
      on adding a scheduling block instance?
      client `set_scheduling_block()` method
- [ ] Add method (non generator) to return 
      scheduling block instance details based
      on scheduling block instance id

## API

- [ ] Review routes in light of Tango Device
      discussion

## Tests

- [ ] !!
