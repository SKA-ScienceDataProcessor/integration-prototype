"""Demo of sending metrics to a Prometheus push gateway."""
import time
import logging

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

logging.basicConfig(level=logging.INFO)


def main():
    """Pushes a Gauge metric to a Prometheus gateway."""
    registry = CollectorRegistry()
    # pylint: disable=no-value-for-parameter, unexpected-keyword-arg
    gauge = Gauge('demo_alarm', 'Demo metric for raising an alarm',
                  registry=registry)

    i = 0
    logging.info('demo app starting')
    while True:
        if i == 1:
            logging.info('raising alarm')
        gauge.set(i)
        push_to_gateway('pushgateway:9091', job='SIP demo', registry=registry)
        time.sleep(60)
        if i == 1:
            i = 0
        else:
            i = 1


if __name__ == '__main__':
    main()
