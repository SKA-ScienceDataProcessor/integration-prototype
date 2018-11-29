# Changelog

All notable changes to the SIP Execution Control Configuration Database 
will be documented in this file.

The format is based on 
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
 [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2018-11-26

### Fixed
- A number of cyclic dependency issues
### Changed
- Updated to `redis==3.0.1`
### Deprecated
- Removed `ConfigDB.set_hash_values()` in favour of the new function
  `ConfigDB.save_dict()` which supports dictionaries being saved 
  hierarchically or flat. The default is currently flat to maintain
  backwards compatibility with versions `<=1.1.5`. 


## [1.1.5] - 2018-11-22

### Added
- Added SchedulingObjectList method to mark a SchedulingObject as complete.


## [1.1.4] - 2018-11-20

### Fixed
- Fixed allowed SDP state transitions.
