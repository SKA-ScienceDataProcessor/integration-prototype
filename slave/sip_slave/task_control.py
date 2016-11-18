# -*- coding: utf-8 -*-
"""This module defines the start (load) and stop (unload) functions for
controlling a SIP task."""
import subprocess
import threading
import time

from sip_common import heartbeat_task, logger
from sip_slave import config


class TaskControl:
    """Class to define the slave task control interface (base class)"""

    def __init__(self):
        """Constructor."""

    def start(self, task):
        """Start (load) the task

        Args:
            task: Task description (name or path?)
        """

    def stop(self, task):
        """Stop (unload) the task

        Args:
            task: Task description (name or path?)
        """

    def set_slave_state_idle(self):
        """Update the slave state (global) to idle.

        The slave state is then sent to the master controller HeartbeatListener
        by the slave controller.
        """
        config.state = 'idle'

    def set_slave_state_busy(self):
        """Update the slave state (global) to busy.

        The slave state is then sent to the master controller HeartbeatListener
        by the slave controller.
        """
        config.state = 'busy'


class TaskControlVisReceiver(TaskControl):
    """Task controller for the visibility receiver.

    - FIXME(BM) Need a good name: perhaps TaskControlProcessPoller

    - Uses subprocess.Popen() to start the task
    - Polls the process to check if it has finished or a certain amount of time
      has passed.
    """
    def __init__(self):
        TaskControl.__init__(self)
        self._poller = None

    def start(self, task):
        """Starts the task and the task poller thread."""
        # Start a task
        logger.info('Starting task {}'.format(task[0]))
        config.subproc = subprocess.Popen(task)

        # Create and start a thread which checks if the task is still running
        # or timed out.
        timeout_s = 60  # FIXME(BM) make this an option!!
        self._poller = self.TaskPoller(self, config.subproc, timeout_s)
        self._poller.start()

    def stop(self, task):
        """Stops (kills) the task"""
        logger.info('unloading task {}'.format(task[0]))
        # FIXME(BM) need to stop the TaskPoller (if its running)!
        # see: http://stackoverflow.com/questions/27102881/python-threading-self-stop-event-object-is-not-callable
        # ... might be ok as daemonic threads are stopped at shutdown
        # see: https://docs.python.org/3/library/threading.html
        # also see: https://mail.python.org/pipermail/python-list/2014-March/668991.html
        # Kill the sub-process
        config.subproc.kill()
        # Reset state
        self.set_slave_state_idle()

    class TaskPoller(threading.Thread):
        """Checks task is still running and has not exceeded a timeout."""
        def __init__(self, task_controller, pid, timeout_s):
            threading.Thread.__init__(self, daemon=True)
            self._task_controller = task_controller
            self._pid = pid
            self._timeout_s = timeout_s

        def run(self):
            """Thread run method."""
            self._task_controller.set_slave_state_busy()
            total_time = 0
            while self._pid.poll() is None:
                time.sleep(1)
                total_time += 1
                # TODO(BM) interaction with slave time-out in HeartbeatListener?
                if self._timeout_s is not None and total_time > self._timeout_s:
                    break
            self._task_controller.set_slave_state_idle()


class TaskControlExample(TaskControl):
    """Task controller which works with the example tasks.

    - Example tasks: tasks/task.py, exec_eng.py
    - Uses subproccess.Popen() to start the task.
    - Checks for states (state1, state2, and busy) from the task and updates
      the slave state (global) based on these to idle or busy.
    """
    def __init__(self):
        TaskControl.__init__(self)

    def start(self, task):
        """load the task

        Some sort of task monitoring process should also be started. For
        'internal' tasks this means checking that the task is sending
        heartbeat messages.
        """
        _state_task = 'off'
        _state_task_prev = 'off'

        # Extract the port number
        port = int(task[1])

        # Start a task
        logger.info('Starting task {}'.format(task[0]))
        config.subproc = subprocess.Popen(task)

        # Create a heartbeat listener to listen for a task
        timeout_msec = 1000
        heartbeat_comp_listener = heartbeat_task.Listener(timeout_msec)
        heartbeat_comp_listener.connect('localhost', port)
        config.poller = self._HeartbeatPoller(self, heartbeat_comp_listener)
        config.poller_run = True
        config.poller.start()

    def stop(self, task):
        """Unload the task"""
        logger.info('unloading task {}'.format(task[0]))

        # Stop the heartbeat poller
        config.poller_run = False

        # Kill the sub-process
        config.subproc.kill()

        # Reset state
        self.set_slave_state_idle()

    class _HeartbeatPoller(threading.Thread):
        """Polls for heartbeat messages from the task

        When it get the message starting, state1, or state2 sets the slave state
        to busy, otherwise set it to off.
        """
        def __init__(self, task_contoller, heartbeat_comp_listener):
            """Constructor."""
            self._task_controller = task_contoller
            self._state_task_prev = ''
            self._heartbeat_comp_listener = heartbeat_comp_listener
            threading.Thread.__init__(self, daemon=True)

        def run(self):
            """Thread run method."""
            while config.poller_run:

                # Listen to the task's heartbeat
                comp_msg = self._heartbeat_comp_listener.listen()

                # Extract a task's state
                state_task = self._get_state(comp_msg)

                # If the task state changes log it
                if state_task != self._state_task_prev:
                    logger.info('**' + comp_msg)
                    self._state_task_prev = state_task

                # Update the controller state
                if state_task == 'starting' or state_task == 'state1' or \
                        state_task == 'state2':
                    self._task_controller.set_slave_state_busy()
                else:
                    config.state = state_task
                time.sleep(1)

        @staticmethod
        def _get_state(msg):
            """Extracts the state from the heartbeat message"""
            tokens = msg.split(" ")
            if len(tokens) < 4:
                tokens = [' ', ' ', ' ', 'off', ' ', ' ']
            return tokens[3]
