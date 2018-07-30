import time
import logging

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

logging.basicConfig(level=logging.INFO)

registry = CollectorRegistry()
g = Gauge('demo_alarm', 'Demo metric for raising an alarm', registry=registry)

i = 0
logging.info('demo app starting')
while True:
    if i == 1:
        logging.info('raising alarm')
    g.set(i)
    push_to_gateway('pushgateway:9091', job='SIP demo', registry=registry)
    time.sleep(60)
    if i == 1:
        i = 0
    else:
        i = 1
