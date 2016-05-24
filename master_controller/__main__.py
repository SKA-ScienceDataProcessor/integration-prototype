""" Master controller main program
"""
from .master_controller import start
from .master_controller import post_event

if __name__ == "__main__":
    """ For testing we simply post events typed on the terminal
    """

    # Create the master controller
    start()

    # Read and process events
    while True:
        event = input('?')
        post_event(event)

