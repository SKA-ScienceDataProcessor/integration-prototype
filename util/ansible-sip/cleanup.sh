#!/bin/bash
if [ -d .vagrant ]; then
    vagrant destroy -f
    rm -rf ./.vagrant
fi
rm -rf ./keys
rm -rf ./roles/GROG.reboot
rm -rf ./roles/angstwad.docker_ubuntu
rm -f  ./*.retry
rm -f  ./playbooks/*.retry
rm -f  ./*.log
rm -f  ./hosts
