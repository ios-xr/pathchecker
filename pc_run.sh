#!/bin/bash

./pathchecker.py --host 6.6.6.6 -u vagrant -p vagrant --port 830 -c 10 -o apphost -a 0 -i GigabitEthernet0/0/0/0 -s 2.2.2.2  -j 8 -l 5 -f -t 10
