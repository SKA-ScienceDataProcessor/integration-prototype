# Visibility ingest workflow script

## Introduction

This is a visibility ingest workflow script which uses the asyncio 
Python SPEAD API to enable concurrent receive of data from a number of 
UDP streams and a set of blocking worker threads to process the data.
This, and the use of double buffering, allows receive and ingest 
processing to operate in the same Python process and therefore memory 
space which should improve performance over other solutions using separate
receive and ingest processes.
  
## Quick-start

For running instructions see the `README.md` file in the parent folder.
