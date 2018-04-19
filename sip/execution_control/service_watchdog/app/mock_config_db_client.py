# -*- coding: utf-8 -*-
"""Mock client for the Redis Configuration database.

This provides functions for testing the services watchdog
"""

services = {
    'sdp_service.sky_model': 'sky_model',
    'sdp_service.telescope_model': 'telescope_model'},

def get_service_list():
    return [{'name': 'sdp_services.sky_model', 'enabled': 'True'},
            {'name': 'sdp_services.telescope_model', 'enabled': 'True'}]

def get_service_name(name):
    return services[name]['service']

def put_service_health(name, health):
    pass

