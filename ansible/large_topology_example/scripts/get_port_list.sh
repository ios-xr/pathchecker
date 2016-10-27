#!/bin/bash
set -x
device_list=`vagrant status | head -n -4 | tail -n +3 | awk '{print $1}'`

echo "{" > ./device_port_list.json
device_arr=($device_list)
for device in ${device_arr[@]}
do
  fwd_ports=`vagrant port $device | tail -n +5 | awk '{print $1 ";" $4}'`
  echo "\"$device\":{" >> ./device_port_list.json

  port_arr=($fwd_ports)
  for port in ${port_arr[@]}
  do
    guest_port=`echo $port | awk -F ';' '{print $1}'`
    host_port=`echo $port | awk -F ';' '{print $2}'`  
    echo -n "\"$guest_port\":\"$host_port\"" >> ./device_port_list.json
    if ! [[ $port == "${port_arr[-1]}" ]]; then
      echo  "," >> ./device_port_list.json
    else
      echo  "" >> ./device_port_list.json
    fi
  done
  echo -n "}" >> ./device_port_list.json

  if ! [[ $device == "${device_arr[-1]}" ]]; then
      echo  "," >> ./device_port_list.json
  else
      echo  "" >> ./device_port_list.json
  fi
done
echo "}" >> ./device_port_list.json
