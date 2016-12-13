.. _master:

Master Controller
=================

**Source code:** :source:`master/sip_master`

This module defines functions and classes which implement the SIP Master
Controller. The Master Controller is a component of the SDP Local Monitor and
Control (LMC) sub-system and performs the following tasks:

- Managing and starting slaves, see
  :ref:`Resource Manager <common.resource_manager>`,
  :ref:`Slave Control <master.slave_control>` and
  :ref:`Slave Heartbeat listener <master.heartbeat_listener>`.
- Starting tasks, see :ref:`Slave Task Control <master.task_control>`.
- Acts as a state machine to report the global state of SDP, see
  :ref:`Master Controller state machine classes <master.master_states>`.
- Holds the state of slaves,
  see :ref:`Slave state machine classes <master.slave_states>`


Running the Master Controller
-----------------------------

.. _master.main:

:mod:`main`
^^^^^^^^^^^

The Master Controller module defines a ``main()`` function which is used
to create the Master Controller application.

.. autofunction:: master.sip_master.main.main

The current version of the SIP code makes use of this function to create
an application (:source:`master/bin/master`) which is configured to point at
the slave configuration file (:source:`master/etc/slave_map.json`) and
resource configuration file (:source:`master/etc/resources.json`) included in
in the SIP GitHub repository.


.. _master.rpc_service:

:mod:`rpc_service`
^^^^^^^^^^^^^^^^^^

The Master Controller RPC service module implements a ``rpyc.Service`` class
(see `rpyc <https://rpyc.readthedocs.io/en/latest/>`_ library).
This can be used give the Master Controller and RPC interface which can be
connected to in order to issue remote commands. In order to connect to this
interface an ``rpyc`` client must be constructed, an example
of which is shown in the RpcService class documentation below.

.. autoclass:: master.sip_master.rpc_service.RpcService
    :members:
    :private-members:
    :show-inheritance:


The Master Controller State Machine
-----------------------------------

.. _master.master_states:

:mod:`master_states`
^^^^^^^^^^^^^^^^^^^^

This module defines the Master Controller state machine. This state machine
defines the following states, classes which inherit the
``State`` class from :ref:`common.state_machine <common.state_machine>`:

- .. class:: Standby
- .. class:: Configuring
- .. class:: UnConfiguring
- .. class:: Available
- .. class:: Degraded
- .. class:: Unavailable

The state machine machine class define in this module, implements a
:ref:`StateMachine <common.state_machine>` class which
defines the action methods associated with these states.

.. autoclass:: master.sip_master.master_states.MasterControllerSM
    :members:
    :show-inheritance:

Action methods have an associated action class, which defines a
thread that processes the action.

- **online** spawns a :ref:`Configure <master.configure>` thread.
- **cap** spawns a :ref:`Capability <master.capability>` thread.
- **offline** spawns an :ref:`UnConfigure <master.un_configure>` thread.
- **shutdown** spawns a :ref:`Shutdown <master.shutdown>` thread.


**MasterControllerSM state table**

Allowed state transitions are described in the ``state_table`` attribute
of this class. The ``state table`` is a dictionary with a key per
state. The value of each state is a dictionary which defines the events
handled by the state and what the response to the event should be.
The event is described by the key in the state dictionary and the
response is a tuple where the first entry defines if the event should
be accepted (1) or rejected(0), the second entry gives the destination
state, and the third entry gives the name of the transition action method.
If an event is not in the table, it is ignored.

.. literalinclude:: ../../master/sip_master/master_states.py
    :language: python
    :linenos:
    :lines: 85-


.. _master.configure:

:mod:`configure`
^^^^^^^^^^^^^^^^

This module defines the **Configure** class which is a thread run by the
Master Contoller state machine in response to the *online* action.

.. autoclass:: master.sip_master.configure.Configure
    :members:
    :show-inheritance:


.. _master.capability:

:mod:`capability`
^^^^^^^^^^^^^^^^^

This module defines the **Capability** class which is a thread run by the
Master Contoller state machine in response to the *cap* action.

.. autoclass:: master.sip_master.capability.Capability
    :members:
    :show-inheritance:


.. _master.un_configure:

:mod:`un_configure`
^^^^^^^^^^^^^^^^^^^

This module defines the **UnConfigure** class which is a thread run by the
Master Contoller state machine in response to the *offline* action.

.. autoclass:: master.sip_master.un_configure.UnConfigure
    :members:
    :show-inheritance:


.. _master.shutdown:

:mod:`shutdown`
^^^^^^^^^^^^^^^

This module defines the **Shutdown** class which is a thread run by the
Master Contoller state machine in response to the *shutdown* action.

.. autoclass:: master.sip_master.shutdown.Shutdown
    :members:
    :show-inheritance:


Controlling slaves
------------------

:mod:`slave_control`
^^^^^^^^^^^^^^^^^^^^

.. _master.slave_control:

.. automodule:: master.sip_master.slave_control
    :members:
    :show-inheritance:

.. _master.heartbeat_listener:

:mod:`heartbeat_listener`
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: master.sip_master.heartbeat_listener
    :members:
    :show-inheritance:

.. _master.task_control:

:mod:`task_control`
^^^^^^^^^^^^^^^^^^^

.. automodule:: master.sip_master.task_control
    :members:
    :show-inheritance:

.. _master.slave_states:

:mod:`slave_states`
^^^^^^^^^^^^^^^^^^^

.. automodule:: master.sip_master.slave_states
    :members:
    :show-inheritance:
