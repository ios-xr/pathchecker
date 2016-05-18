#!/usr/bin/env python
import sys,os,subprocess
from argparse import ArgumentParser
from ncclient import manager
from jinja2 import Template
from lxml import etree
import logging
import pdb
import threading,time

ospf_cost_request = Template("""<config>
      <ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-ospf-cfg">
        <processes>
          <process>
            <process-name>{{OSPF_PROCESS_NAME}}</process-name>
            <default-vrf>
              <area-addresses>
                <area-area-id>
                  <area-id>{{AREA_ID}}</area-id>
                  <name-scopes>
                    <name-scope>
                      <interface-name>{{INTERFACE}}</interface-name>
                      <cost>{{COST}}</cost>
                    </name-scope>
                  </name-scopes>
                </area-area-id>
              </area-addresses>
            </default-vrf>
          </process>
        </processes>
      </ospf>
</config>""")

COST_THRESHOLD = 20 
COST_THRES_EXCEEDED = 0
BACKOFF_STARTED = 0
BACKOFF_INTERVAL = 5
TIMER_DONE = 0

def backoff_timer(start):
    global BACKOFF_STARTED
    global TIMER_DONE

    if start:
        """ 
        Start the backoff timer
        """
        BACKOFF_STARTED = 1
        TIMER_DONE = 0
        thread = threading.Thread(target=run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()
    else:
        BACKOFF_STARTED = 0

def run():
    global TIMER_DONE
    global BACKOFF_INTERVAL

    time.sleep(BACKOFF_INTERVAL)
    TIMER_DONE = 1
    return

def write_state_to_file():
    global COST_THRES_EXCEEDED
    with open('/home/cisco/cost_exceeded_state', 'w') as state_file:
        state_file.write(str(COST_THRES_EXCEEDED))


def monitor_link_state():
    """
    Issue a periodic iperf run to monitor the links state, take action and write state to file
    """

    global COST_THRES_EXCEEDED
    global BACKOFF_STARTED
    global COST_THRESHOLD

    try:
        with open('/home/cisco/cost_exceeded_state', 'r') as state_file:
            COST_THRES_EXCEEDED = int(state_file.readline())
    except Exception as e:
        print "Error while opening state file, let's assume low cost state"
        COST_THRES_EXCEEDED = 0
        write_state_to_file()

    try:
       if COST_THRES_EXCEEDED == 0:
           print "Currently, on reference link %s" %(REF_INTERFACE)
       else:
           print "Currently, on backup link "

       if iperf_run():
            if COST_THRES_EXCEEDED == 0:
                COST_THRES_EXCEEDED = 1
                write_state_to_file()
                print "Woah! iperf run reported discrepancy, increase cost of reference link !"
                take_cost_action(COST_THRES_EXCEEDED)
            else:
                if BACKOFF_STARTED:
                    print "iperf is still showing a problem, backoff timer is already running, revert back if TIMER is done"
                    if TIMER_DONE:
                        #Reverting
                        COST_THRES_EXCEEDED = 0
                        take_cost_action(COST_THRES_EXCEEDED)
                        write_state_to_file()
                        backoff_timer(0)
                    else:
                        print " Backoff timer is still running, wait for the next run"
                else:
                    print "iperf is showing a problem, start a backoff timer before you revert back"
                    backoff_timer(1)            
    except Exception as e:
        print "Problem handling event. For debugging purposes, the state of the variables are:"
        print "COST_THRES_EXCEEDED = %d, \nCOST_THRESHOLD = %d, \nBACKOFF_STARTED = %d\n"  % (COST_THRES_EXCEEDED, COST_THRESHOLD, BACKOFF_STARTED)
        print "error message is"
        print e

    return

def iperf_run():
    # The destination parameter for iperf client may be provided by the app itself.

    if os.getenv("IPERF_SERVER"):
        server = os.getenv('IPERF_SERVER')
    else:
        server = SAMPLE_SERVER 

    if os.getenv("IPERF_INTERVAL"):
        interval = os.getenv("IPERF_INTERVAL")
    else:
        interval = SAMPLE_INTERVAL
  
    print "Starting an iperf run....." 
    cmd ="iperf -c %s -t %d -i %d -u -y C" % \
                    (server, interval, interval)

    try:
        # Perform the network monitoring task 
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        print out
    except Exception as e:
        print "Failed to perform the network monitoring task"
        print e
        sys.exit(1)

    #Parse the output
    try:    
        transferred_bytes = float(out.splitlines()[2].split(',')[7])
        bps = (transferred_bytes * 8) / float(interval)

        bw = bps/1024.0
        jitter = out.splitlines()[2].split(',')[9]
        pkt_loss = out.splitlines()[2].split(',')[12] 
 
        print "bw is"
        print bw
        print "jitter is"  
        print jitter 
        print "pkt_loss is"  
        print pkt_loss   
        verdict = any([float(bw) < float(BW_THRES), float(jitter) > float(JITTER_THRES), float(pkt_loss) > float(PKT_LOSS_THRES)])

        print "verdict is"
        print verdict
    except Exception as e:
        print "iperf failed to gather data. This could be failure on the iperf front or on the link"
        print "Die silently unless the force flag is set, in which case, set the ospf cost"
        if args.force_verdict:
            verdict = True
        else:
            verdict = False
 
    return verdict


def ospf_set_intf_cost(m, ospf_process_name, area_id, interface_name, cost):
    """Simple example to update cost of an OSPF interface

    """
    if m is None or ospf_process_name is None or  area_id is None or interface_name is None or cost is None:
        print >>sys.stderr, "Not enough parameters to update interface cost!"
    data = ospf_cost_request.render(OSPF_PROCESS_NAME=ospf_process_name,
                               AREA_ID=area_id,
                               INTERFACE=interface_name,
                               COST=cost)
    m.edit_config(data,
                  format='xml',
                  target='candidate',
                  default_operation='merge')
    m.commit()

def do_template(m, t, **kwargs):
    data = t.render(kwargs)
    m.edit_config(data,
                  format='xml',
                  target='candidate',
                  default_operation='merge')
    m.commit()

def take_cost_action(cost_state):
     if cost_state:
         cost = COST_THRESHOLD+10
         print "Increasing cost of the reference link %s" %(REF_INTERFACE)   
     else:
         cost = COST_THRESHOLD-10
         print "Decreasing cost of the reference link %s" %(REF_INTERFACE)
     ospf_set_intf_cost(m, OSPF_PROCESS_NAME, AREA_ID, REF_INTERFACE,cost)

        
if __name__ == '__main__':

    parser = ArgumentParser(description='Specify the parameters to influence interface cost for ospf:')

    # Input parameters
    parser.add_argument('--host', type=str, required=True,
                        help="The device IP or DN")
    parser.add_argument('-u', '--username', type=str, default='cisco',
                        help="Go on, guess!")
    parser.add_argument('-p', '--password', type=str, default='cisco',
                        help="Yep, this one too! ;-)")
    parser.add_argument('--port', type=int, default=830,
                        help="Specify this if you want a non-default port")
    parser.add_argument('-c', '--cost', type=str, 
                        help="Specify an interface cost")
    parser.add_argument('-o', '--ospf-process-name', type=str, 
                        help="Specify the ospf process name")
    parser.add_argument('-a', '--area-id', type=str,
                        help="Specify the ospf area")
    parser.add_argument('-i', '--interface', type=str,
                        help="Specify the ospf interface name")
    parser.add_argument('-s', '--iperf-server', type=str,
                        help="Specify the iperf server ip address")
    parser.add_argument('-b', '--bw-threshold', type=str,
                        help="Specify the BW threshold")
    parser.add_argument('-j', '--jitter-threshold', type=str,
                        help="Specify the jitter threshold")
    parser.add_argument('-l', '--pkt-loss-threshold', type=str,
                        help="Specify the pkt loss threshold")
    parser.add_argument('-t', '--iperf_interval', type=int,
                        help="Specify the duration of an iperf run")
    parser.add_argument('-f', '--force-verdict', action='store_true', 
                        help="Force ospf cost change in case of iperf failure")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Do I really need to explain?")


    args = parser.parse_args()

    if args.verbose:
        handler = logging.StreamHandler()
        for log in ['ncclient.transport.ssh', 'ncclient.transport.session', 'ncclient.operations.rpc']:
            logger = logging.getLogger(log)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

    #
    # Could use this extra param instead of the last four arguments
    # specified below:
    #
    # device_params={'name': 'iosxr'}
    #
    def iosxr_unknown_host_cb(host, fingerprint):
        return True

    if args.bw_threshold:
        BW_THRES = args.bw_threshold
    else:
        BW_THRES = 400

    if args.jitter_threshold:
        JITTER_THRES = args.jitter_threshold
    else:
        JITTER_THRES = 10

    if args.pkt_loss_threshold:
        PKT_LOSS_THRES = args.pkt_loss_threshold
    else:
        PKT_LOSS_THRES = 2

    if args.iperf_interval:
        SAMPLE_INTERVAL = args.iperf_interval
    else:
        SAMPLE_INTERVAL = 10 

    if args.iperf_server:
        SAMPLE_SERVER = args.iperf_server
    else:
        SAMPLE_SERVER = "2.2.2.2"

    OSPF_PROCESS_NAME = args.ospf_process_name
    AREA_ID = args.area_id
    REF_INTERFACE = args.interface 

    m =  manager.connect(host=args.host,
                     port=args.port,
                     username=args.username,
                     password=args.password,
                     allow_agent=False,
                     look_for_keys=False,
                     hostkey_verify=False,
                     unknown_host_cb=iosxr_unknown_host_cb)

    while True:
        try:
            monitor_link_state()
        except Exception as e:
            print "Error occured while monitoring the link"
            print "The error message is:"
            print e 
