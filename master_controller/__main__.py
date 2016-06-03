""" Master controller main program

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 6 events; "online", "offline", "configure done", "unconfigure done"
and "error". "online" and "offline" are external and the others are
generated internally.
"""
__author__ = 'David Terrett + Brian McIlwrath'


if __name__ == "__main__":
    from .states import sm
    import threading

    """ This starts the rpyc 'ThreadedServer' - this creates a new 
        thread for each connection on the given port
    """
    from .MasterControllerService import MasterControllerService
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(MasterControllerService,port=12345)
    t = threading.Thread(target=server.start)
    t.start()

    """ For testing we can also run events typed on the terminal
    """
    # Read and process events
    while True:
        event = input('?')
        result = sm.post_event([event])
        if result == 'rejected':
            print('not allowed in current state')
        if result == 'ignored':
            print('command ignored')
        else:
            print('master controller state:', sm.current_state())

