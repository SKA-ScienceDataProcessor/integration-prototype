import json
import os
from pprint import pprint

from .docker_compose_generator.compose_generator import generate_compose_file
from docker_client import DockerClient

DC = DockerClient()




# Obtain workflow stage configuration
path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(path, "utils/mock_workflow.json"), 'r') as f:
    config = json.load(f)


# Generate and verify the compose file
stage_index = 1
pprint(config['stages'][stage_index])
assert config['stages'][stage_index]['type'] == 'processing'
compose_file = generate_compose_file(config['stages'][stage_index])
print(compose_file)

config_path = os.path.join(path, 'docker-compose.dev.yml')
DC.create_services(config_path)