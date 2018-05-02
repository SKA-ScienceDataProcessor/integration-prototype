# Vis ingest workflow definition

Workflow based on Airflow?

<https://airflow.apache.org/configuration.html#scaling-out-with-celery>









## Old?

Attempt at writing a JSON workflow based on hyperflow to represent
a simple visibility ingest workflow.

This needs to start receive and ingest processing
tasks / processes at the same time but these have a dependency in that 
processing uses data produced by the receive.

This schema defines the workflow as a set of processes and signals.


References:
- https://airflow.apache.org/configuration.html#scaling-out-with-celery
- <https://en.wikipedia.org/wiki/Scientific_workflow_system>
- <https://github.com/dice-cyfronet/hyperflow/blob/develop/schemas/workflow.schema.json>
- <https://github.com/dice-cyfronet/hyperflow/wiki>
- <file:///Users/bmort/Downloads/PaaSage-DASPOS-v1.pdf>
- <http://dice.cyfronet.pl/news_presentations/04_HyperFlow-cgw15.pdf>
- <https://github.com/StanfordBioinformatics/JsonWf>
