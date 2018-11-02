# -*- coding: utf-8 -*-
"""High Level Master Controller Client API"""

import ast
from config_db import configDB

class masterClient():
    """ Master Controller Client Interface"""
    def __init__(self):
        self._db = configDB()

    def get_value(self, name, field):
        """Get value in string """
        value = self._db.get_hash(name, field)
        if value:
            return value
        else:
            return None

    def get_value_bool(self, name, field):
        """ Get the value in boolean"""
        value = self.get_value(name, field)
        return bool(value)

    def get_value_all(self, name):
        """Get all the value in the name.
        Returned in dict"""
        value = self._db.get_hash_all(name)
        if value:
            return value
        else:
            return None

    def get_service_list(self, key):
        """ Get all the service list"""
        list = self._db.get_list(key)
        if list:
            for service_list in list:
                list_eval = ast.literal_eval(service_list)
                yield list_eval
            return list_eval
        else:
            None

    def get_service_from_list(self, key, index):
        """ Get the n'th element of the service list.
        If the does not point to an element 0 is return"""
        element = self._db.get_element(key, index)
        if element:
            element_eval = ast.literal_eval(element)
            return element_eval
        else:
            return 0

    def get_service_from_list_bool(self, name, index):
        """ Get the n'th element of the service list in boolean.
        If the does not point to an element 0 is return"""
        element = self.get_service_from_list(name, index)
        for e in element:
            if element[e] == 'true' or 'false' or 'True' or 'False':
                bool(element[e])
            return element

    def get_service_list_length(self, key):
        """ Returns the number of elements in a list
        If the does not point to a list 0 is return"""
        list_length = self._db.get_length(key)
        if list_length:
            return list_length
        else:
            return 0

    def convert_path(self, name):
        path = name.split('.')
        return path

    def add_service_to_list(self, key, element):
        """ Adds a new service to the end of the list"""
        self._db.add_element(key, element)

    def update_value(self, path, field, value):
        """" """
        self._db.set_value(path, field, value)

    def update_service(self, v_path, field, value):
        """ Update the service"""
        # Converts a value from the database to a service path list
        path = self.convert_path(v_path)
        self._db.set_value(path, field, value)
