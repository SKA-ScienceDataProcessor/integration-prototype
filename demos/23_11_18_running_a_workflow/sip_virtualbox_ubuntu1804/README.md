# Scripts for testing SIP in an Ubuntu 18.04 VM

```bash
vagrant up
vagrant ssh

sudo apt-get update
sudo apt install -y python3-pip
# install docker (https://do.co/2FR2PSg)
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install -y docker-ce
sudo usermod -aG docker ${USER}
sudo su - ${USER}
git clone https://github.com/SKA-ScienceDataProcessor/integration-prototype.git
cd integration-prototype
git checkout updates/demos_23_11_18
docker swarm init
docker stack deploy -c deploy/demos_23_11_18/docker-compose.yml sip
docker service ls
./deploy/demos_23_11_18/scripts/get_itango_prompt
lsdev

vagrant destroy -f 
```
