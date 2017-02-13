.. role:: bash(code)
    :language: bash

.. role:: style1
    :class: class1

.. role:: style2
    :class: class2

.. _Installation:

============
Installation
============

Installation Steps
==================

The following sections present some notes which aim to provide a basic
walk through of the steps required to configure a new Linux installation for
running the SIP code. This is followed by some notes specific to configuring
the SIP code to run within a VirtualBox Ubuntu 16.04 Server guest OS.

Download the SIP code
---------------------

If you do not already have a copy of the SIP code clone it from the
`GitHub repository <https://github.com/SKA-ScienceDataProcessor/integration-prototype>`_
using the following command::

    git clone git@github.com:SKA-ScienceDataProcessor/integration-prototype.git

Install Docker
--------------

SIP uses Docker containers for running some parts of the code. The Docker
website provides fairly good install instructions for most operating systems
on the following link: `<https://docs.docker.com/engine/installation/>`_

The basic steps to install and set up Docker for the current (non-root) user
on Ubuntu 16.04 Server is as follows:

.. code:: bash

    sudo apt-get update
    sudo apt-get install apt-transport-https ca-certificates
    sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 \
        --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | \
        sudo tee /etc/apt/sources.list.d/docker.list
    sudo apt-get update
    sudo apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual
    sudo apt-get install docker-engine
    sudo service docker start
    sudo groupadd docker
    sudo usermod -aG docker $USER

To test the install log out and back in again to refresh group membership
(or su - $USER). Then run:

.. code:: bash

    docker run hello-world

Set up SSH authorised keys
--------------------------

In order to use SSH slaves, SIP requires that the node running the
Master Controller can into slave nodes without requiring a password. This can
be done by creating an RSA authentication key for the Master Controller node
and adding the contents of the public key file created (``~/.ssh/id_rsa.pub``)
to the ``~/.ssh/authorized_keys`` file on each slave.

Note that SIP may also use localhost as a SSH slave node so the public key
for the machine which is running the Master Controller should also be added to
its own authorised keys file. For example:

.. code:: bash

    ssh-keygen -t rsa  # Creates RSA key
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys   # Append the public key to authorized keys
    chmod og-wx ~/.ssh/authorized_keys  # Fix permissions on keys file.

If this works you should now be able to SSH into localhost (and any other
slave machine you have configured) without needing a password. ie.
``ssh localhost``, should not prompt for a password.


Install SIP dependencies
------------------------

SIP requires that the following dependencies are installed:

- Python3
- Python3 pip
- Boost Python
- Boost Program_options
- Boost System

On Ubuntu 16.04, these can be installed with the following command::

    sudo apt-get install -y python3-pip libboost-python-dev \
        libboost-program-options-dev libboost-system-dev

SIP also requires that a number of Python dependencies are installed. After
installing Python pip, the ``requirements.txt`` file in the top level SIP code
directory can be used to install the required python dependencies as follows::

    pip3 install -U pip
    pip3 install -r /path/to/sip/requirements.txt


Build Docker container(s)
-------------------------

SIP currently requires that a docker container is build to run the Master
Controller. This should be built with the following command

.. code:: bash

    docker build -f slave/Dockerfile -t slave_controller .

which needs to be run from the top level of the SIP code directory.


VirtualBox: Ubuntu 16.04 Server
===============================

These are some notes on setting up an Ubuntu 16.04 Server guest in VirtualBox.
*This has been tested with a macOS Sierra (10.12.2) host using VirtualBox 5.1.12.*

    - VirtualBox VM set with have 4GB or RAM, 2 CPU cores and 8 GB of HDD.
    - The Ubuntu 16.04 Server iso was downloaded from
      `<https://www.ubuntu.com/download/server>`_.
    - OpenSSH was enabled during the install.

Install guest additions
-----------------------

- Start Ubuntu VM & insert Guest Additions CD image (from Devices menu ->
  Install Guest Additions)
- Mount the CD :bash:`sudo mount /dev/cdrom /media/cdrom`
- Install build tools and dependencies::

    sudo apt-get install -y dkms build-essential linux-headers-generic - linux-headers-$(uname -r)

- Build and install the guest additions::

    sudo /media/cdrom/VBoxLinuxAdditions.run

Network Configuration
---------------------

The VM was configured to have two network adapters, NAT and a host only
network. The host only network was set up in the VirtualBox
preferences (Network -> Host-only Networks) to be configured by a DHCP
server with::

    Server address: 192.168.56.100
    Server mark:    255.255.255.0
    Lower address:  192.168.56.101
    Upper address:  192.168.56.254

In order to bring up the host-only network interface, once logged into the VM,
edit ``/etc/network/interfaces`` and add the following lines::

    auto enp0s8
    iface enp0s8 net dhcp

*It is possible the host-only network adapter has a different name to enp0s8,
if so you can find its name with the command ``ifconfig -a`` or
``ip link show``*

With OpenSSH installed, it is then possible to SSH into the Ubuntu Server
after starting it::

    VBoxManage startvm [name|uuid] -type headless

with::

    ssh [user]@192.168.56.[101..254]

Where ``[user]`` should be replaced with the user account set up during
installation of the VM, and ``[101..254]`` should be replaced with the ip
address assigned to the host-only network adapter (which will be 101 for the
first VM started, 102 for the second etc.).

If you are doing this regularly it is a good idea to set up a hostname for the
VM by adding the following lines to ``/etc/hosts`` on the host OS::

    # Ubuntu 16.04 Server VM's
    192.168.56.101 vm1
    192.168.56.102 vm2
    ...

You can then log into the vm with::

    user@vm1

UDP Socket Buffer Size
----------------------

The default UDP socket buffer size on Ubuntu 16.04 Server is only 208 kiB,
and this will result in dropped packets when streaming data using SPEAD.
To change it to 32 MiB, add these lines to /etc/sysctl.conf:

net.core.rmem_max = 33554432
net.core.rmem_default = 8388608

Reboot the virtual machine and check that the change was applied by
inspecting /proc/sys/net/core/rmem_max

Oxford SKA Nodes
================

TODO...