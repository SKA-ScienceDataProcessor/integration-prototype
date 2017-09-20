# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Unit test naming conventions. All unit tests files should be suffixed with
  with `_test.py`. A single convention simplifies the automated test discovery,
  and avoids the confusion between unittests and test utility classes which 
  sometimes use the prefix `test_`. For more information see 
  [SIP: Unit test naming convensions](https://confluence.ska-sdp.org/display/WBS/SIP%3A+Unit+test+naming+conventions).
- Various PEP-8 and PyLint errors in unit tests   
 
## [0.2.1] - 2017-09-12
### Fixed
- Jenkinsfile to work around a bug in the code where hanging docker services results in the Jenkins server crashing.

## [0.2.0] - 2017-09-08
### Added
- Changelog file. This will be used from now on to keep a top level summary of 
  changes. Versions will also be tagged as GitHub releases.
### Changed
- Updated to version 0.2.0.
### Fixed
- Various pep8 / pylint errors problems in `setup.py`
