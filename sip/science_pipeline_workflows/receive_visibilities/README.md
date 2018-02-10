# SIP Visibility Receive

## Introduction

TODO


## Testing on P3

How to provision and run visibility ingest pipeline in P3 using 3 
receivers and 3 senders.

### 1. Create a Swarm Cluster 

Create swarm cluster with 1 master node and 6 workers either by using the web
UI or CLI

Check if swarm cluster was created successfully

```bash
docker node ls
```

TO interact with the cluster via the docker client.Follow the instructions
on this link <https://confluence.ska-sdp.org/display/WBS/Container+Clusters>

If not, add the workers to the swarm mode - Instructions can be found in the
following link <https://docs.docker.com/engine/swarm/swarm-tutorial/add-nodes/>

### 2. Ansible: Configuring the hosts file

Update hosts file with the correct hostname and IP address under swarm leader 
and swarm worker

------------------------------------------------

### 3. Ansible: Update docker stack and config file

The visibility sender config file are in the 
`/emulators/csp_visibility_sender_02/etc` directory. Update 
`vis_sender_config_1.json`, `vis_sender_config_1.json` and 
`vis_sender_config_2.json` file with the correct IP Address.

Make sure to use network IP (10.0.0.x) and not the floating IP. The network 
can be found by 

```bash
docker node inspect <nodename>
```

------------------------------------------------

### 4. Ansible: Provision the cluster

```bash
ansible-playbook -i hosts playbooks/p3_site.yml
```

------------------------------------------------

### 5. Docker Stack: Run the service 

Deploy the docker stack for the receiver from the `receive_visibilties` folder

```bash
docker stack deploy -c docker-stack.yml receiver
```

Then deploy the docker stack for the sender from the 
`emulators/csp_visibility_sender_02` folder

```bash
docker stack deploy -c docker-stack.yml sender
```

Each node will be created its own local volume. Data written can be found 
inside `/var/lib/docker/volumes/<volume name>/_data`


The logs of the docker service can be viewed through

```bash
docker service logs <service name>
```

To remove all the service

```bash
docker stack <stack name>
```

------------------------------------------------

### 6. Troubleshooting

If you see the following error in the logs
dropped incomplete heap 4 (5669764/20930588 bytes of payload)

Then the buffer size needs to be increased and this can be done either by 
updating `main.yml` file inside sip.ingest role or logging into each node 
running the following command

```bash
sysctl net.core.rmem_max=2147483647
sysctl net.core.rmem_default=2147483647
```

------------------------------------------------

### 6. TO DO

1) Use Redis as a configuration database instead of the config file




