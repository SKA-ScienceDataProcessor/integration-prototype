# -*- coding: utf-8 -*-
"""Straw-man API for accessing the Redis Configuration database.
"""

import ast

class config_db:
    """config_db class

    All access to a configuration database is via a config_db object.
    """

    def __init__(self, name=None):
        """ Create a connection to a configuration database.

        If name is None the SDP wide database is used.
        """
        self.db_ = {}

    def handle(self, path):
        """ Returns a handle to the location defined by path

        path is a list of the elements of the absolute path name
        """
        return db_handle_(self.db_, path)


class db_handle_:
    """A db_handle object represents a handle to a location in the database.

    The location in the database can contain either a value or point to
    a location in the naming heirachy.

    """
    def __init__(self, db, path):
        """ Create a database handle.

        path is a list of the elements of the absolute path name.

        Only config_db or db_handle_ objects can create new handles.
        """
        self.db_ = db
        self.path_ = path

    def handle(self, path):
        """ Returns a handle to the location defined by path

        path is a list of the elements of the path name relative to the
        handle. Path elements are strings or integers (donates a element
        of a list).

        If the path does not exist the result is undefined
        """
        return db_handle_(self.db_, self.path_ + path)

    def get(self):
        """Returns the contents of the database that the handle points to.

        The contents can either be a value (as a string) or a nest of dicts
        and lists.
        """
        v = self.db_
        for p in self.path_:
            v = v[p]
        return v

    def get_eval(self):
        """Gets a value from the database to a boolean or number or None
        """
        return ast.literal_eval(self.get())

    def get_path(self):
        """Gets a value from the database as a database path
        """
        return self.to_path_(self.get())

    def set(self, value):
        """Sets the value of the location that the handle points to.

        If the handle does not point to a leaf the result is undefined
        """
        v = self.db_
        for p in self.path_[:-1]:
            v = v[p]
        v[self.path_[-1]] = str(value)

    def length(self):
        """Returns the number of elements in a list.

        If the handle does not point to a list zero is returned.
        """
        v = self.get()
        if type(v) is list:
            return len(v)
        else:
            return 0

    def element_handle(self, n):
        """ Gets a handle to the n'th element of a list.

        If the handle does not point to a list the result is undefined
        """
        return db_handle_(self.db_, self.path_ + [n])

    def add_element(self, value):
        """Add an new entry to the end of a list.

        If the handle does not point to a list the result is undefined
        """
        v = self.get()
        v.append(value)

    def to_path_(self, value):
        """Converts a value from the database to a path list
        """
        raw_path = value.split('.')
        path = []
        for p in raw_path:
            if p.isdigit():
                path.append(ast.literal_eval(p))
            else:
                path.append(p)
        return path
