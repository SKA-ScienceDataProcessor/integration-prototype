""" Master controller main program

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 6 events; "online", "offline", "configure done", "unconfigure done"
and "error". "online" and "offline" are external and the others are
generated internally.

This needs to be replaced by a proper grown-up FSM.
"""
__author__ = 'David Terrett'


if __name__ == "__main__":
    """ For testing we simply post events typed on the terminal
    """
    from ._states import mc

   # Read and process events
    while True:
        event = input('?')
        mc.post_event([event])

