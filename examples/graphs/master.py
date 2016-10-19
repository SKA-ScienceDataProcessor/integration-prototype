""" Create a graph of the master controller state machine

PYTHONPATH must include integration-prototype/common and master

Creates master.dot.

To turn this into a pdf:

    dot -Tpdf master.dot -o master.pdf
"""

import os
os.environ['SIP_HOSTNAME'] = 'localhost'

from sip_master.master_states import MasterControllerSM

sm = MasterControllerSM()
g = sm.get_graph(title="master controller")
g.write("master.dot")

