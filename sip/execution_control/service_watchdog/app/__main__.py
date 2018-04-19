# -*- coding: utf-8 -*-
"""Module main of the services watchdog."""

import ast

def main():
    """Application entry point.

    The watchdog simply sits in a loop looking at the health of all the
    sdp and system services and updates the configuration database
    with the service status and the overall SDP and TANGO status.

    It also updates a timestamp so that the master controller knows that
    the dog hasn't died.
    """

    # Get the list of services (a dictionary)
    services = get_service_list()

    # Loop forever
    white True:

        # For each service, if it is enabled, get it's health
        for s in services:
            if ast.literal_eval(s['enabled']):

                # Get the name of the service from the database
                name = get_service_name(s['name']

                # Get the health of the service
                health = get_health(name)

                # Write it to the database
                put_service_health(name, heath)

if __name__ == '__main__':
    main()
