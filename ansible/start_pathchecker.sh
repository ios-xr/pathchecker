#!/bin/bash

( ( nohup /home/ubuntu/pathchecker/pc_run.sh >>/home/ubuntu/pathchecker_logs 2>&1 ) & )
