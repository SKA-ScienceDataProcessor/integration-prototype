# Changelog

All notable changes to the SIP Processing Block Controller (PBC) will be 
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to 
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2019-01-09
### Changed
- Updated dockerfile to run the PBC as a root user. While not generally a good
  idea this should fix an issue where the Celery worker does not have 
  permission to talk to the docker socket on some linux systems.

## [1.2.6] - 2019-01-07
### Security
- Updated to PyYaml==4.2b4 to address security vulnerability. 

## [1.2.4] - 2018-12/14
### Changed
- Updated to `skasip-docker-swarm==1.0.7`

## [1.2.3] - 2018-12-07
### Changed
- Added optional log_level argument to the `execute_processing_block`
  task which sets the python logging level.

## [1.2.1] - 2018-12-04
### Changed
- Updated to skasip-config-db@1.2.1 (which downgrades to redis 2.10.6 from 
  3.0.1)

## [1.2.0] - 2018-11-29
### Changed
- Updated to skasip-config-db@1.2.0
