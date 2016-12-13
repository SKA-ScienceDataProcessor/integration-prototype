CSP Visibility sender
=====================

The CSP visibility sender implements the visibility data interface between
SDP and CSP as described in the `ICD documents
<https://confluence.ska-sdp.org/pages/viewpage.action?pageId=145653762>`_:

* 100-000000-002_01_LOW_SDP-CSP-ICD
* 300-000000-002_01_MID_SDP-CSP-ICD

It consists of a ``HeapStreamer`` class, which sets up the SPEAD streams
and associated data descriptions, and a ``Simulator`` class which
generates visibility data and sends it using the ``HeapStreamer``. This
module is callable as a result of the ``__main__.py`` script.

.. module:: emulators.csp_visibility_sender.heap_streamer

..  autoclass:: emulators.csp_visibility_sender.heap_streamer.HeapStreamer
    :members:

    ..  automethod:: __init__


.. module:: emulators.csp_visibility_sender.simulator

..  autoclass:: AbstractSimulator
    :members:

..  autoclass:: SimpleSimulator
    :members:

