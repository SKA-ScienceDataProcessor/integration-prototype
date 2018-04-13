# -*- coding: utf-8 -*-
"""High Level Master Controller Client API"""

import ast
from config_db import configDB

class masterClient():
    """ Master Controller Client Interface"""
    def __init__(self):
        print("Master Client")
        self._db = configDB()

    def get_value(self, name, field):
        """Get """
        path = ':'.join(name)
        value = self._db.get_hash(path, field)
        if value:
            return value
        else:
            return None

    def get_value_all(self, name):
        """Get all the value in the name.
        Returned in dict"""
        path = ':'.join(name)
        value = self._db.get_hash_all(path)
        if value:
            return value
        else:
            return None

    def get_service_list(self, name):
        """ Get all the service list"""
        key = ':'.join(name)
        list = self._db.get_list(key)
        if list:
            for service_list in list:
                list_eval = ast.literal_eval(service_list)
                yield list_eval
            return list_eval
        else:
            None

    def get_service_from_list(self, name, index):
        """ Get the n'th element of the service list
        If the does not point to an element 0 is return"""
        key = ':'.join(name)
        element = self._db.get_element(key, index)
        if element:
            element_eval = ast.literal_eval(element)
            return element_eval
        else:
            return 0

    def get_service_list_length(self, name):
        """ Returns the number of elements in a list
        If the does not point to a list 0 is return"""
        key = ':'.join(name)
        list_length = self._db.get_length(key)
        if list_length:
            return list_length
        else:
            return 0

    def convert_path(self, name):
        path = name.split('.')
        service_path = ':'.join(path)
        return service_path

    def add_service_to_list(self, name, element):
        """ Adds a new service to the end of the list"""
        key = ':'.join(name)
        self._db.add_element(key, element)

    def update_state(self, name, field, value):
        """" """
        path = ':'.join(name)
        self._db.set_value(path, field, value)

    def update_service(self, v_path, field, value):
        """ Update the service"""
        # Converts a value from the database to a service path list
        path = self.convert_path(v_path)
        self._db.set_value(path, field, value)