# SIP Prometheus 

Prometheus configured to receive alerts from all the push push gateways
in a Docker swarm.

It has just one alert rule; to raise an alert called "SipStateAlarm" if
the metric "sip\_state" has the value "1".

Additional alerts are added by editing alert\_rules.yml
