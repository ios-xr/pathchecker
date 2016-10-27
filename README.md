# pathchecker

Everything you need to know about running this application on a Vagrant setup with IOS-XR is documented in a hands-on fashion here:  

<https://xrdocs.github.io/application-hosting/tutorials/2016-07-09-pathchecker-iperf-netconf-for-ospf-path-failover/>


This is essentially a quick & dirty netconf client script that changes ospf cost on an interface based on the result of an iperf session on a link through the same interface.
Used with 2 Back-to-back paths between routers, it helps cause failover between paths based on iperf results. This is of course quite usecase specific, but is representative of how more complex failover applications may be designed and hosted on IOS-XR.


A representative test scenario is shown below:

![topology](https://xrdocs.github.io/xrdocs-images/assets/images/ospf-iperf-ncclient.png)

The usage of the application should be obvious based on the options it needs:

```
root@pod5:/home/ubuntu# ./pathchecker.py -h
usage: pathchecker.py [-h] --host HOST [-u USERNAME] [-p PASSWORD]
                        [--port PORT] [-c COST] [-o OSPF_PROCESS_NAME]
                        [-a AREA_ID] [-i INTERFACE] [-s IPERF_SERVER]
                        [-b BW_THRESHOLD] [-j JITTER_THRESHOLD]
                        [-l PKT_LOSS_THRESHOLD] [-t IPERF_INTERVAL] [-f] [-v]

Specify the parameters to influence interface cost for ospf:

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           The device IP or DN
  -u USERNAME, --username USERNAME
                        Go on, guess!
  -p PASSWORD, --password PASSWORD
                        Yep, this one too! ;-)
  --port PORT           Specify this if you want a non-default port
  -c COST, --cost COST  Specify an interface cost
  -o OSPF_PROCESS_NAME, --ospf-process-name OSPF_PROCESS_NAME
                        Specify the ospf process name
  -a AREA_ID, --area-id AREA_ID
                        Specify the ospf area
  -i INTERFACE, --interface INTERFACE
                        Specify the ospf interface name
  -s IPERF_SERVER, --iperf-server IPERF_SERVER
                        Specify the iperf server ip address
  -b BW_THRESHOLD, --bw-threshold BW_THRESHOLD
                        Specify the BW threshold
  -j JITTER_THRESHOLD, --jitter-threshold JITTER_THRESHOLD
                        Specify the jitter threshold
  -l PKT_LOSS_THRESHOLD, --pkt-loss-threshold PKT_LOSS_THRESHOLD
                        Specify the pkt loss threshold
  -t IPERF_INTERVAL, --iperf_interval IPERF_INTERVAL
                        Specify the duration of an iperf run
  -f, --force-verdict   Force ospf cost change in case of iperf failure
  -v, --verbose         Do I really need to explain?
root@pod5:/home/ubuntu# 
```

## Using Ansible

To solve this problem using Ansible and automate your steps in the same way as you would on actual routers, check out the `ansible/` directory and the corresponind README.md
The we use with Ansible is:  
![topo](https://xrdocs.github.io/xrdocs-images/assets/images/ansible_pathchecker.png)  

The relevant README.md:
<https://github.com/ios-xr/pathchecker/blob/master/ansible/README.md>




## For Larger Topologies
We reuse the Ansible playbook defined above to extend to larger topologies very easily. For this purpose a 6 router topology setup is used under the `ansible/large_topology_example/` folder, as shown below: 
![topo](https://xrdocs.github.io/xrdocs-images/assets/images/pathchecker_large_topo.png)

The relevant README.md is here: 
<https://github.com/ios-xr/pathchecker/blob/master/ansible/large_topology_example/README.md>

 
