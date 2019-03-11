# SIP Pulsar Receiver

## Description

The task of the pulsar search pipeline is to take all of the pulsar candidates 
identified in the processing done by CSP and then further filter those to 
come up with the subset of most likely pulsar candidates.

This scripts uses ftp to receive and perform processing on pulsar 
data streamed from CSP.

More details can be found in C.1.2.2.1.1.1 Pulsar Search.

## Quick Start

### Sender


```bash

python3 -m csp_pss_sender.app /csp_pss_sender/etc/pulsar_sender_config.json


```

### Receiver 

```bash

python3 -m receive_pss.pulsar_search_task 

```

Note. The sender and receiver outdated, it requires to be updated before 
getting before running it. 


