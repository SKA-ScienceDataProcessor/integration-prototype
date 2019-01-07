# Changelog

All notable changes to the SIP Processing Controller (Scheduler) 
will be documented in this file.

The format is based on 
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
 [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.4] - 2019-01-07

### Security
- Updated packages to PyYaml==4.2b4 to fix security vulnerability.
  - skasip-config-db, skasip-pbc, pyyaml versions updated.

## [1.2.3] - 2018-12-14

### Changed
- Updated to `skasip-pbc==1.2.4`

## [1.2.2] - 2018-12-10

### Changed
- Updated to use the SIP PBC library `skasip-pbc==1.2.3`
- Updated the PB queue item data order.
- Added additional check of the overall status of the PC health.
- Updated scheduler code for modified pb_queue item methods. 
- Released new version of the Docker image 
  (`skasip/processing_controller:1.2.2`) 

## [1.2.1] - 2018-12-04

### Changed
- Updated to skasip-config-db==1.2.1
- Updated to use the SIP Processing Block Controller library from pypi,
  skasip-pbc==1.2.1

## [1.2.0] - 2018-11-29

### Changed
- Updated to skasip-config-db@1.2.0
