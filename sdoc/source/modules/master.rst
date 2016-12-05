==============
``sip.master``
==============

The Master Controller is a part of the SDP Local Monitor and Control (LMC)
sub-system and has the responsibility of:

- Managing computing resources (via the Resource Manager).
- Starting computing resources (via the Slave Control).
- Starting tasks (via the Task Control).
- Interfacing with the Telescope Manager.

In the SIP code, the Master Controller is a python module consisting of the
following sub-modules.

.. contents::
   :local:
   :depth: 1

The Master Controller also provides Python script with a ``main()`` function
which provides the the Master Controller service binary.


.. automodule:: sip_master.main

RPC service
-----------

.. automodule:: sip_master.rpc_service
    :members:
    :show-inheritance:

Heartbeat Listener
------------------

.. automodule:: sip_master.heartbeat_listener
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members:


Slave Control
-------------

.. automodule:: sip_master.slave_control
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members:

Task Control
------------

.. automodule:: sip_master.task_control
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members:


Master States
-------------

.. automodule:: sip_master.master_states
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members:


Configure
---------

.. automodule:: sip_master.configure
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members:

Un-configure
------------

.. automodule:: sip_master.un_configure
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members:



Slave States
------------

.. automodule:: sip_master.slave_states
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members:

