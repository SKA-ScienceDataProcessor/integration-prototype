# SIP Prometheus Alarm Receiver Service

The alarm receiver is a WebHook application which listens for HTML PUTs from
Prometheus and inserts the JSON describing an alert into a Kafka queue. The
Kafka topic is "SIP-alarms".
