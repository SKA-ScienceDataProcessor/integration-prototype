# -*- coding: utf-8 -*-
"""High Level Master Controller Client API."""
import ast

from .config_db_redis import ConfigDb


class MasterDbClient:
    """Master Controller Client Interface."""

    def __init__(self):
        """Initialise the Master Controller Database client."""
        self._db = ConfigDb()

    ###########################################################################
    # Get functions
    ###########################################################################

    def get_value(self, key, field):
        """Get value associated to the field in string."""
        value = self._db.get_hash_value(key, field)
        if value:
            return value
        return None

    def get_value_bool(self, key, field):
        """Get the value associated to the field in boolean."""
        value = self.get_value(key, field)
        return bool(value)

    def get_all_value(self, key):
        """Get all the value associated to the name, returned in dict."""
        value = self._db.get_hash_dict(key)
        if value:
            return value
        return None

    def get_service_list(self, key):
        """Get the service list from the database."""
        # Initialise empty list
        list_eval = []

        services = self._db.get_list(key)
        if services:
            for service_list in services:
                list_eval.append(ast.literal_eval(service_list))

        # TODO: (NJT) Need to test this function to check if it returns list
        return list_eval

    def get_service_from_list(self, key, index):
        """Get the n'th element of the service list.

        If the does not point to an element 0 is returned.
        """
        element = self._db.get_list_value(key, index)
        if element:
            element_eval = ast.literal_eval(element)
            return element_eval
        return 0

    def get_service_from_list_bool(self, key, index):
        """Get the n'th element of the service list in boolean.

        If the does not point to an element 0 is returned.
        """
        service = self.get_service_from_list(key, index)
        for entry in service:
            if service[entry] == 'true' or 'false' or 'True' or 'False':
                bool(service[entry])
            return service

    def get_service_list_length(self, key):
        """Get the length of the service list.

        If the does not point to a list 0 is returned.
        """
        list_length = self._db.get_list_length(key)
        if list_length:
            return list_length
        return 0

    ###########################################################################
    # Add functions
    ###########################################################################

    def add_service_to_list(self, key, element):
        """Add a new service to the end of the list."""
        self._db.prepend_to_list(key, element)

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_value(self, key, field, value):
        """Update the value of the given name and field."""
        self._db.set_hash_value(key, field, value)

    def update_service(self, v_path, field, value):
        """Update the service."""
        # Converts the name format
        path = self._convert_path(v_path)
        self._db.set_hash_value(path, field, value)

    ###########################################################################
    # Private functions
    ###########################################################################

    @staticmethod
    def _convert_path(key):
        """Convert the name format to the match the database."""
        key_path = key.split('.')
        service_path = ':'.join(key_path)
        return service_path
