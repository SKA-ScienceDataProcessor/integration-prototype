""" Create a graph of the master controller state machine

PYTHONPATH must include integration-prototype/common and master

Creates master.dot.

To turn this into a pdf:

    dot -Tpdf master.for -o master.pdf
"""

import os
os.environ['SIP_HOSTNAME'] = 'localhost'

from sip_master.states import state_table
from sip_common.state_machine import StateMachine
from sip_master.states import state_table
from sip_master.states import Standby

sm = StateMachine(state_table, Standby)
g = sm.get_graph(title="master controller")
g.write("master.dot")

