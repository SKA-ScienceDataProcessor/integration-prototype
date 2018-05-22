[![Build Status](https://travis-ci.com/SKA-ScienceDataProcessor/integration-prototype.svg?branch=master)](https://travis-ci.com/SKA-ScienceDataProcessor/integration-prototype)

# SDP Integration Prototype

## Introduction

The SDP Integration prototype is a project to develop a lightweight prototype 
of the major components of the SDP system. The focus of this work is to:

- provide verification, testing and analysis of the SDP architecture,
- test external and internally facing SDP software interfaces,
- provide limited tests of horizontal scaling on a representative SDP hardware 
  prototype, the SDP performance prototype platform (P3) also known as ALaSKA.

## The SIP Code

The code in this repository is designed to provide a set of loosely coupled 
services, example workflows and pipelines, and supporting libraries. These 
are intended to be independently testable but also capable of being combined
as part of a larger deployment for testing various combination of the SDP 
software components. 

This repository also consists of a number of emulators which are used 
to provide synthetic data to mock or test various interfaces.

The main SIP code can be found in the `sip` directory and is organised 
according to a structure inspired by the SDP high-level architecture
module view. Emulator code can be found in the `emulators` directory.

As, by design, code folders in this repository are loosely coupled most will 
contain a `README.md` describing their function and how they can be run
and tested. In fact, while folders are grouped into this single repository for
convenience, the majority of sub-directories in this repository can be equally
thought of as standalone sub-repositories. 
 
In order to test collections of SIP code which providing various test 
deployments scripts facilitating this can be found in the `deploy` directory 
and at higher levels in the code tree. 

