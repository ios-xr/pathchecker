#!/bin/bash

yum-config-manager --add-repo http://devhub.cisco.com/artifactory/xr600/3rdparty/x86_64
yum install -y iperf
