Developer notes
===============

TODO(BM) this page needs a lot of work still...

Master Controller
-----------------
- What is the role of the Master Controller?
- How does Master Controller interacts with slaves?
- How does the Master controller interact with tasks?
- Role of resource manager

Slave (Controller) activity diagram
-----------------------------------

TODO(BM)

Slaves
------
- What is a SIP slave?
- How to creating a new slave type?

Tasks
-----
- What is a SIP task

Creating a new task
^^^^^^^^^^^^^^^^^^^

TODO(BM) this section needs quite a lot of work and testing and ideally
creating a tutorial task.

The most basic steps required to add a new task are as follows.

1. Create an executable task script in the ``sip/tasks`` folder.
2. Add configuration to the ``sip/etc/slave_map.json`` task. This
   configuration file registers the task with the Master Controller and
   associates it with a slave type and slave task control module.

Depending on the type of task it may be required to add a new slave
task control module class. The task control modules, which are defined in
``sip/slave/task_control.py``, set the policy for how a slave runs the
task.

More development work will be needed to define new slave types.

Logging
-------
- Programming model used for logging
- Sending log messages
- The log aggregator service
- Log filters

