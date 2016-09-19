#!/usr/bin/env python

import json
import subprocess, shlex
import os, paramiko
import pdb

import logging

logging.basicConfig(level=logging.DEBUG)

from netmiko import ConnectHandler

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
HOST="10.0.2.2"

with open('/vagrant/device_port_list.json') as data_file:
    device_ports = json.load(data_file)


def transfer_keys(rtr_lnx_port, filename):
    remote_client = paramiko.SSHClient()
    remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_client.connect(HOST, port=int(rtr_lnx_port), username='vagrant', password='vagrant')

    sftp = remote_client.open_sftp()
    remote_file="/home/vagrant/id_rsa.pub"
    local_file="/vagrant/id_rsa.pub"
    sftp.put(local_file, remote_file)

    remote_file="/home/vagrant/id_rsa_pub.b64"
    local_file="/vagrant/id_rsa_pub.b64"
    sftp.put(local_file, remote_file)
    sftp.close()

    #  Place the base64 key in the disk0:/ folder
 
    cmd = "sudo cp /home/vagrant/id_rsa_pub.b64 /disk0:/id_rsa_pub.b64" 
    stdin, stdout, stderr = remote_client.exec_command(cmd)
    remote_client.close()
    

#Transfer public key to authorized keys file
def xr_linux_import_pubkey(rtr_lnx_port, filename):
    remote_client = paramiko.SSHClient()
    remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_client.connect(HOST, port=int(rtr_lnx_port), username='vagrant', password='vagrant')

    # Add the key to the authorized keys folder
    cmd = "cat /home/vagrant/id_rsa.pub >> /home/vagrant/.ssh/authorized_keys" 
    stdin, stdout, stderr = remote_client.exec_command(cmd)
    remote_client.close()


# Use netmiko to directly apply base64 to XR
def xr_import_b64_key(rtr_port, filename):
    cisco_ios_xrv = {
      'device_type': 'cisco_xr',
      'ip':   HOST,
      'username': 'vagrant',
      'password': 'vagrant',
      'port' : rtr_port,          # optional, defaults to 22
      'secret': 'secret',     # optional, defaults to ''
      'verbose': False,       # optional, defaults to False
    }

    net_connect = ConnectHandler(**cisco_ios_xrv)

    key_path="id_rsa_pub.b64"
    try:
      output = net_connect.send_command('crypto key import authentication rsa disk0:/'+key_path)
    except:
      print "Key already added to remote node"
       

for device in device_ports:
    if 'rtr' in str(device):
      try:
        transfer_keys(device_ports[str(device)]["57722"], "id_rsa.pub")
        xr_linux_import_pubkey(device_ports[str(device)]["57722"], "id_rsa.pub")
      except Exception as e:
        print "In all likeliness, the router - "+str(device)+" isn't up yet"
        print "Error is "+ str(e)

#      xr_import_b64_key(device_ports[str(device)]["22"], "id_rsa_pub.b64")

