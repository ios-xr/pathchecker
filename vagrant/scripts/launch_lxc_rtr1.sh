#!/bin/bash

mkdir /misc/app_host/rootfs
tar -zxf /misc/app_host/scratch/pathchecker_rootfs.tar.gz -C /misc/app_host/rootfs/

sudo -i virsh create /home/vagrant/pathchecker.xml
