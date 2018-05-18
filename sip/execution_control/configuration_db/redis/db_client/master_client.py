# -*- coding: utf-8 -*-
"""High Level Master Controller Client API"""

import ast
from config_db_redis import ConfigDB

class MasterClient():
    """ Master Controller Client Interface"""
    def __init__(self):
        print("Master Client")
        self._db = ConfigDB()


    # #############################################################################
    # Get functions
    # #############################################################################


    def get_value(self, name, field):
        """Get value associated to the fiedl in string"""
        path = ':'.join(name)
        value = self._db.get_value(path, field)
        if value:
            return value
        else:
            return None

    def get_value_bool(self, name, field):
        """ Get the value associated to the field in boolean"""
        value = self.get_value(name, field)
        return bool(value)

    def get_all_value(self, name):
        """Get all the value associated to the name, returned in dict"""
        path = ':'.join(name)
        value = self._db.get_all_field_value(path)
        if value:
            return value
        else:
            return None

    def get_service_list(self, name):
        """ Get the service list from the database"""
        key = ':'.join(name)
        list = self._db.get_list(key)
        if list:
            for service_list in list:
                list_eval = ast.literal_eval(service_list)
                yield list_eval
        else:
            None

    def get_service_from_list(self, name, index):
        """ Get the n'th element of the service list.
        If the does not point to an element 0 is return"""
        key = ':'.join(name)
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

    def get_service_list_length(self, name):
        """ Get the length of the service list.If the does not point
        to a list 0 is return"""
        key = ':'.join(name)
        list_length = self._db.get_length(key)
        if list_length:
            return list_length
        else:
            return 0


    # #############################################################################
    # Add functions
    # #############################################################################


    def add_service_to_list(self, name, element):
        """ Adds a new service to the end of the list"""
        key = ':'.join(name)
        self._db.add_element(key, element)


    # #############################################################################
    # Update functions
    # #############################################################################


    def update_value(self, name, field, value):
        """"Updates the value of the given name and field"""
        path = ':'.join(name)
        self._db.set_value(path, field, value)

    def update_service(self, v_path, field, value):
        """ Update the service"""
        # Converts the name format
        path = self._convert_path(v_path)
        self._db.set_value(path, field, value)


    # #############################################################################
    # Private functions
    # #############################################################################


    def _convert_path(self, name):
        """Converts the name format to the match the database."""
        path = name.split('.')
        service_path = ':'.join(path)
        return service_path
