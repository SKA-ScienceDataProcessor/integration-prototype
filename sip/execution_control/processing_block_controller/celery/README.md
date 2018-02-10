# SIP Processing Block Controller

## Roles

1. Executes a processing block. The processing block contains a number of
   workflow stages defined by the workflow dictionary argument passed
   to the Processing Block Controller instance (Celery task).
2. In order to Execute a processing block this component will need to 
   interact with various Platform Services APIs likely abstracted though 
   an interface or a set of interfaces.

