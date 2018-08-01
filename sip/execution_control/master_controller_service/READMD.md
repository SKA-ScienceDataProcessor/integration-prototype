# SIP Master Controller Service (REST variant)

Previously master\_controller/mock\_watchdog

## Resources (in DB)
* __W__ Current state of SDP
* __R__ Target (commanded SDP state [target_state in mock\_watchdog])
* __W__ Target state of component *NAME* (component specific
state - e.g. tell processing controller to stop processing)
* __R__ Current state of components (services)
    * _NOTE:_ Initial implementation of 1 or 2 of the following from the EC:
        1. Processing Controller (Scheduler) - includes wrapped up state of processing block controllers
        1. Monitoring & logging services(s)

## Activities
* Update state of SDP
* Update component target states
* Update current state of components (services)

## Other Activities
* Interrogate the state of components
