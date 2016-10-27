#!/bin/bash

echo "nameserver 171.70.168.183" >> /etc/resolv.conf
yum-config-manager --add-repo http://devhub.cisco.com/artifactory/xr600/3rdparty/x86_64
yum install -y iperf

