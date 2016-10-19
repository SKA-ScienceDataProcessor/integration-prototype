""" Create a graph of the slave controller state machine

PYTHONPATH must include integration-prototype/common and master

Creates slave.dot.

To turn this into a pdf:

    dot -Tpdf slave.dot -o slave.pdf
"""

import os
os.environ['SIP_HOSTNAME'] = 'localhost'

from sip_master.slave_states import SlaveControllerSM

sm = SlaveControllerSM()
g = sm.get_graph(title="slave controller")
g.write("slave.dot")

