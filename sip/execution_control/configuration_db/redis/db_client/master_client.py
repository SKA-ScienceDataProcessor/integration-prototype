# -*- coding: utf-8 -*-
"""High Level Master Controller Client API."""
import ast

from .config_db_redis import ConfigDbRedis


class MasterClient:
    """Master Controller Client Interface"""

    def __init__(self):
        self._db = ConfigDbRedis()

    ###########################################################################
    # Get functions
    ###########################################################################

    def get_value(self, name, field):
        """Get value associated to the field in string"""
        path = ':'.join(name)
        value = self._db.get_hash_value(path, field)
        if value:
            return value
        return None

    def get_value_bool(self, name, field):
        """Get the value associated to the field in boolean"""
        value = self.get_value(name, field)
        return bool(value)

    def get_all_value(self, name):
        """Get all the value associated to the name, returned in dict"""
        path = ':'.join(name)
        value = self._db.get_hash_dict(path)
        if value:
            return value
        return None

    def get_service_list(self, name):
        """Get the service list from the database"""
        key = ':'.join(name)
        services = self._db.get_list(key)
        if services:
            for service_list in services:
                list_eval = ast.literal_eval(service_list)
                yield list_eval

    def get_service_from_list(self, name, index):
        """Get the n'th element of the service list.
        If the does not point to an element 0 is return"""
        key = ':'.join(name)
        element = self._db.get_list_value(key, index)
        if element:
            element_eval = ast.literal_eval(element)
            return element_eval
        return 0

    def get_service_from_list_bool(self, name, index):
        """Get the n'th element of the service list in boolean.
        If the does not point to an element 0 is return"""
        service = self.get_service_from_list(name, index)
        for entry in service:
            if service[entry] == 'true' or 'false' or 'True' or 'False':
                bool(service[entry])
            return service

    def get_service_list_length(self, name):
        """Get the length of the service list.If the does not point
        to a list 0 is return"""
        key = ':'.join(name)
        list_length = self._db.get_list_length(key)
        if list_length:
            return list_length
        return 0

    ###########################################################################
    # Add functions
    ###########################################################################

    def add_service_to_list(self, name, element):
        """Adds a new service to the end of the list"""
        key = ':'.join(name)
        self._db.prepend_to_list(key, element)

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_value(self, name, field, value):
        """"Updates the value of the given name and field"""
        path = ':'.join(name)
        self._db.set_hash_value(path, field, value)

    def update_service(self, v_path, field, value):
        """Update the service"""
        # Converts the name format
        path = self._convert_path(v_path)
        self._db.set_hash_value(path, field, value)

    ###########################################################################
    # Private functions
    ###########################################################################

    @staticmethod
    def _convert_path(name):
        """Converts the name format to the match the database."""
        path = name.split('.')
        service_path = ':'.join(path)
        return service_path
