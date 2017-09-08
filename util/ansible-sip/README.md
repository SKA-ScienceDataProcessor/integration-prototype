## Scripts to provision and deploy SIP

* Requires Ansible >= 2.2.0
* Provisioning a cluster of VMs requires Vagrant >= 1.9.0 and Virtualbox >= 5.0
* Ansible scripts expect Ubuntu 16.04 hosts

------------------------------------------------

##### TODO:
* OpenStack Heat template for AlaSKA-P3
* Spark Cluster Ansible roles & plays
* Mesos (+ Marathon, ...) Ansible roles & plays 
* Create official ansible-galaxy role for SIP (and other custom roles)

------------------------------------------------

### 1. Introduction

The following scripts can be used to provision and deploy SIP.
This is split into two stages:
1. Provisioning the cluster.
2. Configuration of the cluster with the SIP software stack.

#### 1.1 Quickstart

Two scripts are provided for very quick deployment and destruction of the SIP 
development environment.
* `bootstrap.sh` Creates a default set of SIP VMs and configures sets them
  up with the SIP software stack.
* `cleanup.sh` Tears down the VMs and removes all temporary files.
 
------------------------------------------------

### 2. Provisioning the cluster.

The scripts provide two options for configuring a cluster with SIP:
1. Using Vagrant to create VMs with Virtualbox.
2. Using OpenStack to create baremetal instances on AlaSKA-P3

#### 2.1 Vagrant

##### 2.1.1 Configuration

A `Vagrantfile` is provided which will create and configure a cluster of one 
or more Ubuntu-16.04 VirtualBox VMs. The Cluster configuration is specified 
near the top of the `Vagrantfile` in the section labeled `Settings`.
Feel free to modify the values in this section. Of note are the number of
CPUs and memory allocated to each VM and the list of VM's to be created.
The list of VMs is specified by the `boxes` array which contains a Ruby Hash
for each VM to be created. 

The Hash specifying a VM is required to have the 
following keys:

* **name**: specifying the hostname of the VM
* **groups**: specifies the groups to which the host should belong. Currently
  supported values are *swarm_leader*, *swarm_worker*, and *swarm_manager*.
  A single host must be designated as a the *swarm_leader*.   
* **ip**: The IP address of the host. This is the IP address allocated to the 
  VM. Each host should be given a unique IP address.
* **cpus**: The number of CPUs to allocate to the VM.
* **memory**: The memory in MiB to allocate to the VM.

Options below the `boxes` array should be considered advanced options and are
not likely to have to be modified.

##### 2.1.2 Starting the cluster

The Vagrant cluster can be started with the following command:
```bash
$ vagrant up
```

##### 2.1.3 Cleaning up the cluster

The Vagrant cluster can be removed with the following command:
```bash
$ vagrant destory -f
```

##### 2.1.4 Other (useful) Vagrant commands
To list the status of VMs:
```bash
$ vagrant status
```
In order to SSH into a VM:
```bash
$ vagrant ssh [hostname]
```
It is also possible to ssh into the VMs without vagrant using the command:
```bash
$ ssh -i keys/sip_key -o IdentitiesOnly=yes ubuntu@[ip]
```

To suspend (sleep) the VMs
```bash
$ vagrant suspend
```
To wake up (resume) the VMs
```bash
$ vagrant resume
```


#### 2.2 OpenStack

TODO

------------------------------------------------

### 3. Ansible: Configuring the SIP software stack

A set of Ansible plays are provided to install the SIP software stack onto the 
cluster provisioned in section 2.

These depend on a number of Ansible roles which should be installed prior to 
running the playbook with the command:

```bash
$ ansible-galaxy install -r requirements.yml --roles-path roles
```

This will download the required roles into the local roles folder.

Once the roles have been installed the SIP software stack can be then installed
with the Ansible playbook `site.yml` which is found in the `playbooks` 
directory. This is run with the following command:

```bash
$ ansible-playbook -i hosts playbooks/site.yml
```

The `hosts` file will have been created when provisioning the cluster by the 
Vagrant or OpenStack scripts. 

------------------------------------------------

### 4. Troubleshooting

#### 4.1 SSH errors when trying to connect to VMs or when running Ansible.
* Clear out IP addresses in `~/.ssh/known_hosts for hosts that have been 
  defined in the `hosts` file.
* Clear out your ssh-agent, either one key at a time or with `ssh-add -D`. You
  can list keys stored in the agent with `ssh-add -l`

