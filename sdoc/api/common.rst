
Common functions
================

- Module: :mod:`sip.common`
- Source code: :source:`sip/common`

This module defines a number of common functions used throughout the SIP
library. This includes

- :ref:`Logging <common.logging>`
- :ref:`Heartbeat message functions <common.heartbeat>`
- :ref:`A state machine base class <common.state_machine>`
- :ref:`A resource manager <common.resource_manager>`


.. _common.logging:

Logging
-------

SIP provides a number of logging modules for publishing and subscribing to
python logging messages.

Publishing of log messages is provided by :mod:`logging_api` and
:mod:`logging_handlers` modules, and aggregation of log messages in a
logging server is provided by the :mod:`logging_aggregator` module.

The :mod:`logging_server` script provides a main function which is be used as
a Logging server service for aggregating logging messages from the rest of the
SIP modules.


Logging API module
^^^^^^^^^^^^^^^^^^
This module provides an implementation of a Python logging class specialised
to be used by SIP modules for publishing log messages.

**Basic Usage:**

.. code-block:: python

    from sip.common.logging_api import log
    log.info('my info message')

This functionality is implemented by overriding a default Python
``logging.Logger`` object and ``logging.LogRecord`` and attaching a specialsed
``logging.Handler`` defined in the :mod:`logging_handlers` module.

.. autoclass:: sip.common.logging_api.SipLogger
    :members:
    :show-inheritance:

.. autoclass:: sip.common.logging_api.SipLogRecord
    :members:
    :show-inheritance:

Logging Handlers
^^^^^^^^^^^^^^^^

.. automodule:: sip.common.logging_handlers
    :members:
    :show-inheritance:

Logging Aggregator
^^^^^^^^^^^^^^^^^^

.. automodule:: sip.common.logging_aggregator
    :members:
    :show-inheritance:

Logging Aggregator (Server) Service application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: sip.common.logging_server
    :members:
    :show-inheritance:

.. _common.heartbeat:

Heartbeat messages
------------------

Slave Heartbeats
^^^^^^^^^^^^^^^^

The sender class does ...

.. autoclass:: sip.common.heartbeat.Sender
    :members:


.. autoclass:: sip.common.heartbeat.Listener
    :members:

Task Heartbeats
^^^^^^^^^^^^^^^

.. automodule:: sip.common.heartbeat_task
    :members:
    :show-inheritance:

.. _common.state_machine:

State Machines
--------------

.. automodule:: sip.common.state_machine
    :members:
    :show-inheritance:


.. _common.resource_manager:

Resource Manager
----------------
.. automodule:: sip.common.resource_manager
    :members:
    :show-inheritance:
