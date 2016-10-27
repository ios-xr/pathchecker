#!/bin/bash

( ( nohup iperf -s -u 1>/dev/null 2>&1 ) & )

