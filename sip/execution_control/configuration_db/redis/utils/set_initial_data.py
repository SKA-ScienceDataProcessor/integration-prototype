# -*- coding: utf-8 -*-
""" Set initial data to the configuration database"""

from jsonschema import validate
import simplejson as json
from flatten_json import flatten

import sys
import os
import ast


from app.config_api import ConfigInit


def main():
    """Add initial data to the database"""
    print("Adding Initial Data")

    with open('utils/initial_data.json', 'r') as f:
        schema_data = f.read()
    init_data = json.loads(schema_data)

    db = ConfigInit()
    db.set_init_data(init_data)

    print("Data Added")


if __name__ == '__main__':
    main()