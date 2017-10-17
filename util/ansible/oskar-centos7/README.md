# Ansible plays to install OSKAR on CentOS7

## Introduction

The following scripts define a set of Ansible roles for installing OSKAR
on Centos 7. A Vagrantfile is also provided for testing a VirtualBox VM.

## Requirements

- Ansible. Install with: `sudo pip install ansible`.
- Vagrant [optional, for testing with VMs]. Install from:
  <https://www.vagrantup.com/downloads.html>.

## Starting a VirtualBox Centos 7 VirtualBox VM

A Vagrantfile is provided which will create a Virtualbox machine configured
for centos7. To download and and start the VM issue the following command:

```bash
vagrant up
```

To SSH into the VM use the following command:

```bash
vagrant ssh
```

or alternatively, the following command will also ssh into the VM:

```bash
ssh -i ./.vagrant/machines/default/virtualbox/private_key vagrant@127.0.0.1 -p 2222
```

In order to remove the VM to clean up, use the command:

```bash
vagrant destroy -f
```

## Installing OSKAR using the Ansible play

Once the hosts have been provisioned (eg. using Vagrant as described above),
OSKAR can be installed using the provided Ansible script as follows:

```bash
ansible-playbook -i [inventory file] --private-key=[key file] site.yml
```

If testing with a VM creating using Vagrant, the `[inventory file]`
would be the provided `hosts.vagrant` and the `[key file]` would be
the private key of the VM managed by Vagrant, ie.
`.vagrant/machines/default/virtualbox/private_key`. If running on AlaSKA P3
you will need to create an inventory file which adhers to the description found
at <http://docs.ansible.com/ansible/latest/intro_inventory.html>. The
`[key file]` will be the private key used to provision the OpenStack instances.
