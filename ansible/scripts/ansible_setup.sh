#!/usr/bin/env bash
http_proxy=$1
https_proxy=$2
SET_PROXY=`export http_proxy="$http_proxy" && https_proxy="$http_proxy"`

$SET_PROXY && sudo -E apt-get update
$SET_PROXY && sudo -E apt-get install -y python-setuptools python-dev build-essential git libssl-dev libffi-dev sshpass lxc
$SET_PROXY && sudo -E apt-get install -y python-pip
$SET_PROXY && sudo -E pip install netmiko pycparser==2.13 idna 

git config --global http.proxy $http_proxy
git config --global https.proxy $https_proxy
git clone https://github.com/ios-xr/iosxr-ansible.git
git clone https://github.com/ansible/ansible.git --recursive

cd ansible/ && sudo python setup.py install
echo "source /vagrant/ansible_pathchecker/ansible_env" >> /home/vagrant/.profile

ssh-keygen -t rsa -f /home/vagrant/.ssh/id_rsa -q -P ""
cut -d" " -f2 /home/vagrant/.ssh/id_rsa.pub | base64 -d > /home/vagrant/.ssh/id_rsa_pub.b64

#Copy the public keys to the shared /vagrant folder
cp /home/vagrant/.ssh/id_rsa.pub /vagrant/
cp /home/vagrant/.ssh/id_rsa_pub.b64 /vagrant/

#Copy the ansible playbooks for pathchecker to the right location
cp -r /vagrant/ansible_pathchecker/* /home/vagrant/iosxr-ansible/remote/

