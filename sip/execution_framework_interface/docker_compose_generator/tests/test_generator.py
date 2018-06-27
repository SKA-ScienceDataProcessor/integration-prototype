# -*- coding: utf-8 -*-
"""."""
import os

import yaml


def test_generate():
    """Test generating a Docker compose file for visibility send."""
    path = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(path, 'scheduler_config.yml'), 'r') as stream:
        config = yaml.load(stream)

    print(config)
