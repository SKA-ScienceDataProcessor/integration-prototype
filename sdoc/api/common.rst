
Common functions
================

- Module: :mod:`sip.common`
- Source code: :source:`common/sip_common`

This module defines a number of common functions used throughout the SIP
library. This includes

- :ref:`Logging <common.logging>`
- :ref:`Heartbeat message functions <common.heartbeat>`
- :ref:`A state machine base class <common.state_machine>`
- :ref:`A resource manager <common.resource_manager>`


.. _common.logging:

Logging
-------

.. automodule:: sip_common.logger
    :members:
    :show-inheritance:


.. _common.heartbeat:

Heartbeat messages
------------------

Slave Heartbeats
^^^^^^^^^^^^^^^^

The sender class does ...

.. autoclass:: sip_common.heartbeat.Sender
    :members:


.. autoclass:: sip_common.heartbeat.Listener
    :members:

Task Heartbeats
^^^^^^^^^^^^^^^

.. automodule:: sip_common.heartbeat_task
    :members:
    :show-inheritance:

.. _common.state_machine:

State Machines
--------------

.. automodule:: sip_common.state_machine
    :members:
    :show-inheritance:


.. _common.resource_manager:

Resource Manager
----------------
.. automodule:: common.sip_common.resource_manager
    :members:
    :show-inheritance:
