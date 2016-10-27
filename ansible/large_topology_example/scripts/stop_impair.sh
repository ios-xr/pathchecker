#!/bin/bash

echo "Stopping impairment on all the links"
sudo tc qdisc del dev eth3 root &> /dev/null
sudo tc qdisc del dev eth4 root &> /dev/null
