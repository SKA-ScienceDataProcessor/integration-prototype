# -*- coding: utf-8 -*-
"""
    Master Controller Service.

    This version polls REDIS Events rather
    than the database directly.
"""

from time import time, sleep
from sched import scheduler
import random
import json
import logging
import logging.config

from config_db.sdp_state import SDPState
from config_db.service_state import ServiceState

logConfigAsJSON = '''{
    "version": 1,
    "formatters":
    {
        "default":
        {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        }
    },
    "handlers":
    {
        "console":
        {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        }
    },
    "root":
    {
        "level": "DEBUG",
        "handlers": ["console"]
    }
}
'''

SDP = 'sdp_state'
MC = 'MasterController'
PC = 'ProcessingController'
PDC = "ProcessingBlockController"
AL = "Alerts"

sdp_db = SDPState()
mc_db  = ServiceState("ExecutionControl", "MasterController", "test")
pc_db  = ServiceState("ExecutionControl", "ProcessingController", "test")
pdc_db = ServiceState("ExecutionControl", "ProcessingBlockController", "test")
al_db  = ServiceState("ExecutionControl", "Alerts", "test")

substates = ((mc_db,MC),(pc_db,PC),(pdc_db,PDC),(al_db,AL))
state_ready = { MC:False, PC:False, PDC:False, AL:False }
db_handles = { SDP: sdp_db, MC: mc_db, PC: pc_db, PDC: pdc_db, AL: al_db }

def waiting_on_states():
    """
    Look for events from updating current state for each component and 
    set SDP current state when all are set to the target state
    """
    global state_ready
    logger.debug('waiting_on_states')
    event = event_queue.get()
    if event and event.type == 'current_state_updated':
        logger.debug('handling event {}'.format(event.id))
        if event.type == 'current_state_updated':
            service_name = event.object_id 
            logger.debug('have event for {}'.format(service_name))
            for key in state_ready.keys():
                if key in service_name:
                    state_ready[key] = True
            if state_ready[MC] and state_ready[PC] and \
                    state_ready[PDC] and state_ready[AL]:
                logger.debug("Setting current state from target state for SDP State")
                sdp_db.update_current_state(sdp_db.target_state)
                state_ready = { MC:False, PC:False, PDC:False, AL:False }
                # go back to check_event_queue
                sch.enter(0, 1, check_event_queue)
            else:
                sch.enter(0.5, 1, waiting_on_states)
    else:
        sch.enter(0.5, 1, waiting_on_states)

def update_sub_state(ob,name):
    """
    Called by the scheduler this simulates the PC component(s)
    receiving a change state command and changing the state as required.
    """
    logger.debug("(update_sub_state) Setting current state from target state for {}".format(name))
    ts = ob.update_current_state(ob.target_state)



def update_components(target_state):
    """
    When we get a new target state this function is called
    to ensure components receive the target state(s) and act
    on them.
    """

    # ### update component target states. Presumably processing
    # ### controller & processing block controller?
    global state_ready
    wait_on_states = False
    for db,name in substates:
        logger.debug('Setting target state of {} to be {}'.format(name,target_state))
        if db.current_state != target_state:
            db.update_target_state(target_state)
            logger.debug('Schedule {} current state to be updated'.format(name))
            sch.enter(random.random()*5, 1, update_sub_state, argument=(db,name))
            state_ready[name] = False
            wait_on_states = True
        else:
            state_ready[name] = True

    if wait_on_states:
        sch.enter(0.5, 1, waiting_on_states)
    else:
        logger.debug('no need to wait on subsystems')
        sdp_db.update_current_state(sdp_db.target_state)
        sch.enter(0, 1, check_event_queue)

    # What SHOULD we do if the target state is OFF?
    # Everything will go off.
    # For the time being we will run subroutines to change the target
    # states for the subsystems.
    # I will use the scheduler to run the other subroutines at a randomly
    # generated time.
    
    # Presumably in a later version we would actually set target state, eg:
    # db.update_component_state(PC, "Target_state", target_state)
    # We could then use the scheduler schedule another function to check 
    # that they have changed.
    ## this belongs in another routine!!
    #~ db.update_component_state(PC, "Current_state", target_state)
    #~ ## this belongs in another routine!!
    #~ db.update_component_state(LOG, "Current_state", target_state)
    #~ logger.debug('Pretend to do work. New state is {}.'.format(target_state))
    #~ return(target_state)


def handle_event(event):
    """
    Retrieve the target state and update the SDP state.
    """

    try:
        logger.debug('Getting target state')
        target_state = sdp_db.target_state
        if target_state is not None:
            logger.info('Target state is {}'.format(target_state))

            # The target state may only be honored if the current state
            # is a certain value. The correct values can be obtained from
            # the database API so that we do not need to keep separate
            # copies of the legal transitions.
            sdp_state = sdp_db.current_state
            if target_state == sdp_state:
                return
            states = sdp_db.allowed_state_transitions[sdp_state]
            if not states:
                logger.warn('No allowed states; cannot continue')
                return
            if not target_state in states:
                logger.warn('Target state {} not in valide list ({})'.format(target_state,states))
                return
            logger.debug(
                'Communicating target_state to component systems')
            if target_state == 'standby':
                update_components('on')
            else:
                update_components(target_state)
            #~ logger.debug(
              #~ 'Setting SDP_state to be the new state {}.'.
              #~ format(updated_state))
            #~ ts = sdp_db.update_current_state(updated_state)
        else:
            logger.warning('Target state does not exist in database.')
    except Exception as err:
        logger.warning('Exception occured {}'.format(err))


def check_event_queue():
    """
    Poll the Event Queue.
    
    Call handle_event if there is an event of type updated.
    Reset the scheduler to call this function again in 1 second.
    """
    event = event_queue.get()
    logger.debug('Event is {}'.format(event))
    if event and event.type == 'target_state_updated':
        logger.debug('Event ID is {}'.format(event.id))
        handle_event(event)
        return
    # Return to this function after one second
    sch.enter(1, 1, check_event_queue)


if __name__ == '__main__':
    """Application entry point.

    Logging, scheduling, database and database events
    are all set up here.
    DB event queue polling is done by check_event_queue()
    which itself is called by sched.scheduler()
    """
    logging.config.dictConfig(json.loads(logConfigAsJSON))
    logger = logging.getLogger(__name__)
    sch = scheduler(time, sleep)
    try:
        logger.debug("starting")
        for db in ( sdp_db,  mc_db,  pc_db,  pdc_db,  al_db):
            if db.current_state in ('unknown',):
                logger.debug("Required to switch current_state to init")
                db.update_current_state('init')
        subscriber = 'SDP'
        logger.debug('About to register with event queue')
        event_queue = sdp_db.subscribe(subscriber)
        event_queue2 = mc_db.subscribe(MC)
        active_subs = sdp_db.get_subscribers()
        logger.debug('Subscribers: {}'.format(active_subs))
        sch.enter(0, 1, check_event_queue)
        sch.run()
    except KeyboardInterrupt as err:
        logger.debug('Keyboard Interrupt {}'.format(err))
        logger.info('Exiting!')

'''
From https://docs.google.com/document/d/1KEFKL2NHxgt05EqyEUMJkhot6ycwIx1CJ5nRp3hIBFU/edit#heading=h.pafi558x88t1

The primary state that can be reported by the SDP Master device is derived from 
the set of predefined TANGO states inherited by all TANGO Devices. It is for 
this reason that SKA specifies additional state variables, such as health state 
and admin mode. 

The SDP Primary states are:
 - INIT: Reported when the SDP Master TANGO Device is available, but when one 
   or more of the persistent SDP services are still starting up. During this 
   state the SDP will not accept scheduling commands.
 - ON: Reported when the SDP is fully operational and will accept configure 
   commands, which schedule processing on the SDP system.
 - DISABLE:  Reported when the SDP is in a drain state with respect to 
   processing. In this state, the SDP will allow any running Processing 
   Block workflows to complete, but not accept new scheduling commands or 
   start any new Processing Blocks.
 - STANDBY: Reported when SDP is not accepting any new scheduling commands 
   or running any Processing Block workflows.
 - ALARM: Reported when the SDP is still operational but an alarm condition 
   has been triggered.
 - FAULT: Reported when SDP detects an unrecoverable error.
 - OFF: Reported when only the SDP Master TANGO device, Configuration
   Database, and SDP Master Controller is running. The rest of SDP is 
   powered off.
 - UNKNOWN: Reported when the state can not be obtained.

Ben and Nijin have rewritten the database API to enforce the above (and also 
use lower-case letters in the values held in the DB). I think I want to 
enforce the rules myself rather than rely on the DB, on the other hand, all
of the rules can be picked up from the API



For me the Flask will produce the states as in the DB or UNKNOWN when it
cannot find the proper state in the DB.

For now the flask will stay the same; all faults, ie wrong requests, will be
reported to the logs.

System will start in INIT; I will find it in that state.
For now I will ignore ALARM and FAULT states.

When the system "wakes up" it will check for INIT state and request subsystems
to go into STANDBY.
I will rewrite code so that "subsystem" subroutines will change states from 
INIT to STANDBY; another routine will monitor and log their status before
setting its own status to standby when all the subs are set.
'''
