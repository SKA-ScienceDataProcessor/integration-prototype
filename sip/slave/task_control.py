# -*- coding: utf-8 -*-
"""This module defines the interface used to control a SIP task.

This module also contains an implementation to start a task as a subprocess
and poll to check when it has finished, or reached a timeout.

To implement new task controllers, inherit the base class TaskControl and
implement the start() and stop() methods.
"""
import subprocess
import threading
import time
import os
import logging

from sip.common import heartbeat_task
from sip.common.logging_api import log
from sip.slave import config


class TaskControl:
    """Base class to define the slave task control interface."""

    def __init__(self):
        """Constructor."""
        self.settings = None

    def start(self, task, settings):
        """Start (load) the task

        Args:
            task: Task description (name or path?)
            settings: Settings dictionary for the task control object.
        """
        raise RuntimeError("Implement TaskControl.start()!")

    def stop(self):
        """Stop (unload) the task."""
        raise RuntimeError("Implement TaskControl.stop()!")

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

    def set_slave_state_error(self):
        """Update the slave state (global) to error.

        The slave state is then sent to the master controller HeartbeatListener
        by the slave controller.
        """
        config.state = 'error'


class TaskControlProcessPoller(TaskControl):
    """Task controller for the visibility receiver.

    Uses subprocess.Popen() to start the task and polls the process to check
    if it has finished, or a certain amount of time has passed.
    """
    def __init__(self):
        TaskControl.__init__(self)
        self._poller = None
        self.name = ''
        self.subproc = None

    def start(self, task, settings):
        """Starts the task and the task poller thread.

        Args:
            task (string list): Path to the task and its command line arguments.
            settings (dict): Settings dictionary for the task control object.
        """
        # Start a task
        self.name = os.path.normpath(task[0])
        self.settings = settings
        log.info('[TaskControllProcessPoller] Starting task {}'.format(self.name))
        self.subproc = subprocess.Popen(task)

        # Create and start a thread which checks if the task is still running
        # or timed out.
        self._poller = self.TaskPoller(self)
        self._poller.start()

    def stop(self):
        """Stops (kills) the task."""
        log.info('unloading task {}'.format(self.name))

        # Kill the sub-process and the polling thread.
        self._poller.stop_thread()
        self.subproc.kill()

        # Reset state
        self.set_slave_state_idle()

    class TaskPoller(threading.Thread):
        """Checks task is still running and has not exceeded a timeout."""
        def __init__(self, task_controller):
            threading.Thread.__init__(self)
            self._task_controller = task_controller
            self._done = threading.Event()

        def stop_thread(self):
            self._done.set()

        def run(self):
            """Thread run method."""
            self._task_controller.set_slave_state_busy()
            name = self._task_controller.name
            timeout = self._task_controller.settings['timeout']
            total_time = 0
            while (self._task_controller.subproc.poll() is None
                    and not self._done.is_set()):
                time.sleep(1)
                total_time += 1
                # TODO(BM) interaction with slave time-out in HeartbeatListener?
                if timeout is not None and total_time > timeout:
                    log.warn("Task {} timed out".format(name))
                    break

            # TODO(FD) Check we're OK to kill the process here.
            # Possible interaction with master controller UnConfigure.
            self._task_controller.stop()


class TaskControlExample(TaskControl):
    """Task controller which works with the example tasks.

    - Example tasks: tasks/task.py, exec_eng.py
    - Uses subproccess.Popen() to start the task.
    - Checks for states (state1, state2, busy and finished) from the task and
      updates the slave state (global) based on these to idle or busy.
    """
    def __init__(self):
        TaskControl.__init__(self)
        self._poller = None
        self.name = ''
        self._subproc = None

    def start(self, task, settings):
        """load the task

        Some sort of task monitoring process should also be started. For
        'internal' tasks this means checking that the task is sending
        heartbeat messages.

        Args:
            task (string list): Path to the task and its command line arguments.
            settings (dict): Settings dictionary for the task control object.
        """
        self.name = os.path.normpath(task[0])
        _state_task = 'off'
        _state_task_prev = 'off'

        # Extract the port number
        port = int(task[1])

        # Create a heartbeat listener to listen for a task
        timeout_msec = 10000
        heartbeat_comp_listener = heartbeat_task.Listener(timeout_msec)
        heartbeat_comp_listener.connect('localhost', port)
        self._poller = self._HeartbeatPoller(self, heartbeat_comp_listener)
        self._poller.start()

        # Start a task
        log.info('[TaskControlExample] Starting task {}'.format(task[0]))
        self._subproc = subprocess.Popen(task)

    def stop(self):
        """Unload the task."""
        log.info('unloading task {}'.format(self.name))

        # Kill the sub-process and the polling thread.
        self._poller.stop_thread()
        self._subproc.kill()

        # Reset state
        self.set_slave_state_idle()

    class _HeartbeatPoller(threading.Thread):
        """Polls for heartbeat messages from the task

        When it gets a message it sets the state to busy.
        """
        def __init__(self, task_controller, heartbeat_comp_listener):
            """Constructor."""
            threading.Thread.__init__(self)
            self._task_controller = task_controller
            self._state_task_prev = ''
            self._heartbeat_comp_listener = heartbeat_comp_listener
            self._done = threading.Event()

        def stop_thread(self):
            self._done.set()

        def run(self):
            """Thread run method."""
            while not self._done.is_set():

                # Listen to the task's heartbeat - this will wait for up
                # to 10 seconds for a message
                comp_msg = self._heartbeat_comp_listener.listen()

                # An empty message means the listener timed out
                if comp_msg == '':

                    # If the slave isn't in the finished state log the
                    # timeout and put the controller state to error
                    if state_task != 'finished':
                        log.info('Slave task heartbeat timeout')
                        self._task_controller.set_slave_state_error()
                else:

                    # Extract a task's state
                    state_task = self._get_state(comp_msg)

                    # If the task state changes log it
                    if state_task != self._state_task_prev:
                        log.info('Slave task heartbeat message: ''{}'''. \
                                format(comp_msg))
                        self._state_task_prev = state_task

                    # Update the controller state
                    if state_task != 'finished':
                        self._task_controller.set_slave_state_busy()
                    else:
                        self._task_controller.set_slave_state_idle()

            # Set to idle before exiting.
            self._task_controller.set_slave_state_idle()

        @staticmethod
        def _get_state(msg):
            """Extracts the state from the heartbeat message"""
            tokens = msg.split(" ")
            if len(tokens) < 4:
                tokens = [' ', ' ', ' ', '', ' ', ' ']
            return tokens[3]
