#!/bin/bash

vagrant up
ansible-galaxy install -r requirements.yml --roles-path roles
ansible-playbook -i hosts playbooks/site.yml
