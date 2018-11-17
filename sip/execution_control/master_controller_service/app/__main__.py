# -*- coding: utf-8 -*-
"""Master Controller Service.

This version polls REDIS Events rather than the database directly.
"""
from time import time, sleep
from sched import scheduler
import random
import logging

from sip_logging import init_logger
from config_db import SDPState
from config_db import ServiceState

from .__init__ import __version__

SDP = 'sdp_state'
MC = 'MasterController'
PC = 'ProcessingController'
PDC = "ProcessingBlockController"
AL = "Alerts"

SDP_DB = SDPState()
MC_DB = ServiceState("ExecutionControl", "MasterController", "test")
PC_DB = ServiceState("ExecutionControl", "ProcessingController", "test")
PBC_DB = ServiceState("ExecutionControl", "ProcessingBlockController", "test")
AL_DB = ServiceState("ExecutionControl", "Alerts", "test")

SUB_STATES = ((MC_DB, MC), (PC_DB, PC), (PBC_DB, PDC), (AL_DB, AL))
STATE_READY = {MC: False, PC: False, PDC: False, AL: False}
DB_HANDLES = {SDP: SDP_DB, MC: MC_DB, PC: PC_DB, PDC: PBC_DB, AL: AL_DB}

LOG = logging.getLogger('sip.ec.master_controller')
SCH = scheduler(time, sleep)


def break_me():
    """Randomly generate a fault or alarm state for one of the substates."""
    LOG.debug('randomly generate a fault or alarm')
    state = (None, None, None, None, None, 'fault', 'alarm')[
        random.randint(0, 6)]
    if state is not None:
        service = (MC_DB, PC_DB, PBC_DB, AL_DB)[random.randint(0, 3)]
        LOG.debug('Changing random service to %s', state)
        service.update_current_state(state)
    SCH.enter(random.random() * 500, 1, break_me)
    # ~ sch.enter(random.random()*50,1,break_me)


def waiting_on_states():
    """FIXME.

    Look for events from updating current state for each component and
    set SDP current state when all are set to the target state
    """
    global STATE_READY
    LOG.debug('waiting_on_states')
    event = EVENT_QUEUE.get()
    if event and event.type == 'current_state_updated':
        LOG.debug('handling event %s', event.id)
        if event.type == 'current_state_updated':
            service_name = event.object_id
            LOG.debug('have event for %s', service_name)
            for key in STATE_READY:
                if key in service_name:
                    STATE_READY[key] = True
            if all(STATE_READY.values()):
                LOG.debug("Setting current state from target state for "
                          "SDP State")
                SDP_DB.update_current_state(SDP_DB.target_state)
                STATE_READY = {MC: False, PC: False, PDC: False, AL: False}
                # go back to check_event_queue
                SCH.enter(0, 1, check_event_queue)
            else:
                SCH.enter(0.5, 1, waiting_on_states)
    else:
        SCH.enter(0.5, 1, waiting_on_states)


def update_sub_state(ob, name):
    """FIXME.

    Called by the scheduler this simulates the PC component(s)
    receiving a change state command and changing the state as required.

    Args:
        ob (??): ???
        name (??): ????

    """
    LOG.debug("(update_sub_state) Setting current state from target "
              "state for %s", name)
    _ = ob.update_current_state(ob.target_state)


def update_components(target_state):
    """Update component target states.

    When we get a new target state this function is called
    to ensure components receive the target state(s) and act
    on them.
    """
    # ### update component target states. Presumably processing
    # ### controller & processing block controller?
    global STATE_READY
    wait_on_states = False
    for service_state, name in SUB_STATES:
        LOG.debug('Setting target state of %s to be %s', name, target_state)
        _current_state = service_state.current_state
        if (_current_state != target_state and target_state in
                service_state.allowed_state_transitions[_current_state]):
            service_state.update_target_state(target_state)
            LOG.debug('Schedule %s current state to be updated', name)
            SCH.enter(random.random() * 5, 1, update_sub_state,
                      argument=(service_state, name))
            STATE_READY[name] = False
            wait_on_states = True
        else:
            STATE_READY[name] = True

    if wait_on_states:
        SCH.enter(0.5, 1, waiting_on_states)
    else:
        LOG.debug('no need to wait on subsystems')
        SDP_DB.update_current_state(SDP_DB.target_state)
        SCH.enter(0, 1, check_event_queue)


# FIXME(BMo): rename to handle_target_state_updated_event
def handle_target_state_updated_event():
    """Retrieve the target state and update the SDP state."""
    LOG.debug('Getting target state')
    target_state = SDP_DB.target_state
    if target_state is not None:
        LOG.info('Target state is %s', target_state)

        # The target state may only be honored if the current state
        # is a certain value. The correct values can be obtained from
        # the database API so that we do not need to keep separate
        # copies of the legal transitions.
        sdp_state = SDP_DB.current_state
        if target_state == sdp_state:
            return
        states = SDP_DB.allowed_state_transitions[sdp_state]
        if not states:
            LOG.warning('No allowed states; cannot continue')
            return
        if target_state not in states:
            LOG.warning('Target state %s not in valid list (%s)',
                        target_state, states)
            return
            # FIXME(BMo) the line below is unreachable ...?
            # LOG.debug('Communicating target_state to component systems')
        if target_state == 'standby':
            update_components('on')
        else:
            update_components(target_state)
    else:
        LOG.warning('Target state does not exist in database.')


def check_event_queue():
    """Poll the Event Queue for state change events.

    Call handle_event if there is an event of type updated.
    Reset the scheduler to call this function again in 1 second.
    """
    event = EVENT_QUEUE.get()
    LOG.debug('Event is %s', event)
    if event:

        if event.type == 'target_state_updated' \
                and event.object_id == 'sdp_state':
            LOG.debug('Event ID is %s', event.id)
            handle_target_state_updated_event()
            return

        if event.type == 'current_state_updated' \
                and event.object_id != 'sdp_state':
            LOG.debug('Event ID is %s', event.id)
            new_state = event.data['new_state']
            if new_state in ('fault', 'alarm'):
                LOG.warning('We have a %s on %s', new_state, event.object_id)
                if SDP_DB.current_state not in ('disable', 'fault', 'off'):
                    SDP_DB.update_current_state(new_state)
        else:
            pass

    # Return to this function after one second
    SCH.enter(1, 1, check_event_queue)


def main():
    """Start the Master Controller service.

    Logging, scheduling, database and database events are all set up here.

    DB event queue polling is done by the check_event_queue() which is
    registered with a Python Event Scheduler
    (https://docs.python.org/3/library/sched.html)
    """
    pass


if __name__ == '__main__':
    # TODO(BMo) wait for DB to be available

    init_logger()
    # FIXME(BMo) Using globals defined from __main__ makes the code hard \
    #            to follow.
    try:
        LOG.debug("Starting Master Controller (version: %s)", __version__)
        for db in (SDP_DB, MC_DB, PC_DB, PBC_DB, AL_DB):
            if db.current_state in ('unknown',):
                LOG.debug("Required to switch current_state to init")
                db.update_current_state('init')
        SUBSCRIBER = 'ExecutionControl.MasterController'
        LOG.debug('About to register with event queue')
        EVENT_QUEUE = SDP_DB.subscribe(SUBSCRIBER)
        ACTIVE_SUBS = SDP_DB.get_subscribers()
        LOG.debug('Subscribers: %s', ACTIVE_SUBS)
        SCH.enter(0, 1, check_event_queue)
        SCH.enter(100 + random.random() * 500, 1, break_me)
        # sch.enter(50 + random.random()*100, 1, break_me)
        SCH.run()
    except KeyboardInterrupt as err:
        LOG.debug('Keyboard Interrupt %s', err)
        LOG.info('Exiting!')
