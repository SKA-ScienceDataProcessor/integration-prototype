# SIP Alarm Handling - prometheus implementation

## Description

This package is a demonstration of how prometheus could be used as the
mechanism for generating SDP alarms.

It consists of the following components (all deployable as docker containers)

- A demo application, written in Python, that uses the prometheus client API
  to publishs a metric called "demo_alarm" which changes value to either o or
  1 once a minute.

- A "push gateway" that receives metrics from applications and makes them
  available to be "scraped" by prometheus.

- prometheus. This gathers metrics from the push gateways and generates
  alerts on the basis of simple rules. The demo is configured to generate
  an alert whenever "demo_alarm" has the value 1.

- An alert manager that receives alerts from prometheus and applies rules
  (which can involve multiple alerts) to generate alarms and route them
  to alarm receivers. The demo simple generates an alarm whenever the
  demo_alarm alert is received and sends it to the alarm receiver with
  an http POST.

- An alarm receiver which is a WebHook application that writes the alarm 
  (as a JSON string) into a Kafka queue. The topic name is SIP-alarms.

The Kafka broker listens to port 9094 on the host that started the
containers.

## Quick Start

```bash
docker-compose -f docker-compose.yml up -d --build
```

View alarms in the Kafka queue (may take a couple of minutes to appear)
```bash
kafkacat -b 127.0.0.1:9094 -t SIP-alarms
```

Shut down
```bash
docker-compose stop
```

## Python client

To listen for alarms from Python

```python
from kafka import KafkaConsumer
consumer = KafkaConsumer('SIP-alarms',bootstrap_servers='localhost:9094')
for msg in consumer:
    print(msg)
```
