#!/usr/bin/env python
# vim: set fileencoding=utf-8:

import logging
import MySQLdb
import os
import sys
import time

import subprocess

OUT_PORT = 'eth1'
ports = {}

guarantees = {'tap44e21c13-40':{'0':200,'192.168.1.18':150}, 'tap840158bf-03':{'0':600,'192.168.2.14':500}}
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
myfile = file("testit.txt", 'w')

def run_cmd(args):
    logging.debug(" ".join(args))
    return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

def run_vsctl(args):
    full_args = ["ovs-vsctl"] + args
    return run_cmd(full_args)

def run_dpctl(args):
	full_args = ["ovs-dpctl"] + args
	return run_cmd(full_args)

def get_taps():
    args = ['list-ports', 'br-int']
    result = run_vsctl(args)
#    return [i for i in result.strip().split('\n') if i.startswith('tap')]
    return result

def run_tc(args):
    full_args = ["tc"] + args
    return run_cmd(full_args)


def tc_tap_change(pid, rate):
    classid = "1:"+ str(pid)
    rate = str(rate / 1000)+"kbit" 
    tmp = os.popen("tc class show dev "+ OUT_PORT +" | grep "+ classid +" | wc -l").read()
    if int(tmp) > 0:
	os.popen("tc class change dev "+ OUT_PORT + ' parent 1:1 classid ' + classid + ' htb rate ' + str(rate))
    else:
	os.popen("tc class add dev "+ OUT_PORT + ' parent 1:1 classid ' + classid + ' htb rate ' + str(rate))
#tc class change dev eth1 parent 1:1 classid 1:6 htb rate 600mbit

def tc_flow_change(pid, flow_ip, rate):
    flow_id = "1:"+pid + flow_ip.split(".")[-1]
    rate = str(rate / 1000)+"kbit"
    tmp = os.popen("tc class show dev "+ OUT_PORT +" | grep "+ flow_id +" | wc -l").read()
    




def set_db_attribute(table_name, record, column, value):
    args = ["set", table_name, record, "%s=%s" % (column, value)]
    return run_vsctl(args)

def set_interface_ingress_policing_rate(record, value):
    set_db_attribute('Interface', record, 'ingress_policing_rate', int(value))
    set_db_attribute('Interface', record, 'ingress_policing_burst', int(value / 10))

def clear_db_attribute(table_name, record, column):
    args = ["clear", table_name, record, column]
    return run_vsctl(args)
############################################
#Class: Ports and Flows
class PortInfo:
    
    def __init__(self, name='tap0'):
	self.port_name = name
        self.tx_bytes = []
        self.rx_bytes = []
        self.tx_rate = 0
        self.rx_rate = 0
	self.tx_guarantee = 0
	self.rx_guarantee = 0
        self.tx_cap = 1000
        self.rx_cap = 1000
	self.flows = {}
	self.flow_txg = {}
	self.flow_rxg = {}
	#flow_txg = dstIP:guarantee
	#flow: {dstIP:[bytes, rate, cap]}
# For flow: inpoty:6,dstIP:192.168.1.18 ---> in TC:      class_id = 1:6   flow_id = 1:618

    def UpdateTxRate(self, tx):
	if len(self.tx_bytes) > 2:
            self.tx_bytes.pop(0)
        self.tx_bytes.append(int(tx))
	rate = [-1]
	for i in xrange(len(self.tx_bytes) - 1):
            rate.append(self.tx_bytes[i + 1] - self.tx_bytes[i])
	rate.sort()
    	#rate_max = self.tx_bytes[-1] - self.tx_bytes[-2]
        #if self.tx_cap >= 0 and rate_max > self.tx_cap:
        #    rate_max = self.tx_cap
	rate_max = rate[-1] * 10 * 8
	self.tx_rate = rate_max
	#if self.port_name =='tapbbb7fbd5-c8':
	#	myfile = open('txrate.txt', 'a')
	#	myfile.write("%s\n" %rate_max)
	#	myfile.close()

    def UpdateRxRate(self, rx):
	if len(self.rx_bytes) > 2:
            self.rx_bytes.pop(0)
	self.rx_bytes.append(int(rx))
	rate = [-1]
	for i in xrange(len(self.rx_bytes) - 1):
            rate.append(self.rx_bytes[i + 1] - self.rx_bytes[i])
	rate.sort()
    	rate_max = rate[-1]* 10 * 8
	self.rx_rate = rate_max

    def UpdateRates(self, tx, rx):
	self.UpdateTxRate(tx)
	self.UpdateRxRate(rx)
	
    def add_flow(self,dstIP,tx_byte):
	if dstIP in self.flows:
	    self.flows[dstIP].add_txbyte(tx_byte)
	else:
	    self.flows[dstIP] = FlowInfo(dstIP)
	    self.flows[dstIP].add_txbyte(tx_byte)

    def cap_flows(self):
	print "start capping flows"
	used = 0.0
        over = 0.0
        spare = 5000
        total = self.tx_cap
	for fid in self.flows:
	    print "flow for cap :",fid
	    self.flows[fid].update()
	    tx = self.flows[fid].rate * 8
	    if fid in self.flow_txg:
		guarantee = self.flow_txg[fid] * 1000 ** 2
	    else:
		guarantee = 0
	    if tx <= guarantee:
	        used += tx * 1.25 + spare
	    else:
                used += tx
            over += tx - guarantee
        if over <= 0:
            over = used 
	for fid in self.flows:
	    if fid in self.flow_txg:
                guarantee = self.flow_txg[fid] * 1000 ** 2
            else:
                guarantee = 0
	    rate = self.flows[fid].rate * 8
	    cap = guarantee
	    if rate  > guarantee:
                cap = min(total, max(guarantee, (rate + max(0, rate - guarantee) / over * (total  - used))))
	    else:
	        #cap = rate * 1.25 + spare
	        cap = guarantee + spare
	    self.flows[fid].tx_cap = cap
	    print "flow ------:", fid
	    print "rate :", self.flows[fid].tx_rate 
	    print "cap  :", self.flows[fid].tx_cap
	
	

class FlowInfo:
    def __init__(self,dstIP):
	self.dst_ip = dstIP
	self.src_ip = ""
	self.tx_byte = [0,0]
	self.tx_rate = 0
	self.tx_cap = 0

    def add_txbyte(self,byte):
	if len(self.tx_byte.size) <= 2:
	    self.tx_byte.append(int(byte))

    def update(self):
	self.rate = self.tx_byte[1]-self.tx_byte[0]
	if self.rate <= 0:
	    self.rate = 0
	self.tx_byte.pop(0)
 
    



######################################################################
#New ways to get ports and traffic statistics 

def get_ports():
	global ports
	args = ['show', '-s']
	raw_port = run_dpctl(args)
	port_map = {}
	#    return [i for i in result.strip().split('\n') if i.startswith('tap')]
	for i in raw_port.strip().split('port'): #for every port
	    port_info = i.split('		')
	    port_id = port_info[0].split(':')[0]
	    port_id = port_id[1:] 
	    port_name = port_info[0].split(':')[1][1:]
	    if port_name.endswith('\n'):
		port_name = port_name[:-1]
	    port_traffic = port_info[-1].split(' ')
		#['RX', 'bytes:27716431', '(26.4', 'MiB)', '', 'TX', 'bytes:2301368922', '(2.1', 'GiB)\n\t']
	    rx = port_traffic[1].split(':')[-1]
	    tx = port_traffic[-3].split(':')[-1]
	    if tx=='':
		tx = '0'

	    
	    if port_id in ports:
	        ports[port_id].UpdateRates(rx, tx)
	    else:
		if port_name.startswith("tap"):
		    ports[port_id] = PortInfo(port_name)
	   	    ports[port_id].UpdateRates(rx, tx)
		    if port_name in guarantees:
			for i in guarantees[port_name]:
			    if i == '0':
				ports[port_id].tx_guarantee = guarantees[port_name][i]
			    else:
				ports[port_id].flow_txg[i] = guarantees[port_name][i]    
		
#guarantees = {'tap44e21c13-40':[200,{192.168.1.18:150}], 'tap840158bf-03':[600,{192.168.2.10:500}]}

	return raw_port

def get_flows():
    for key in ports:
	tmp = os.popen("ovs-dpctl dump-flows br-int | grep 'in_port(" + key +")'").read()
	for flow in tmp.split("\n"):
	    flow_info = flow.split(",")
	    flow_dst = ""
	    flow_byte = ""
	    for info in flow_info:
		if info.startswith("ipv4"):
		    flow_dst = flow_info[(flow_info.index(info) + 1)].split("=")[-1]
		if info.startswith(' bytes'):
		    flow_byte = info.split(":")[-1]
	    if flow_dst != "":
	        ports[key].add_flow(flow_dst, flow_byte)	
		print "adding flows from get flow:", flow_dst
	
	
	

#	args = ['dump-flows', 'br-int ']
#	raw_flow = run_dpctl(args)
#	print "Now get flows:::"
#	print raw_flow
#	return raw_flow

#######################################################################


def update_port_caps():
    global ports
    global guarantees
    used = 0.0
    over = 0.0
    spare = 5000
    total = 1000 ** 3
    for pid in ports:
	print "-----------"
	#all in bits
	tx = ports[pid].tx_rate
	guarantee = ports[pid].tx_guarantee * 1000 ** 2
	if tx <= guarantee:
	    used += tx * 1.25 + spare
	else:
            used += tx
        over += tx - guarantee
    if over <= 0:
        over = used
    for pid in ports:
	guarantee = ports[pid].tx_guarantee * 1000 ** 2
        cap = guarantee
	rate = ports[pid].tx_rate
        if rate  > guarantee:
            cap = min(total, max(guarantee, (rate + max(0, rate - guarantee) / over * (total  - used))))
	else:
	    #cap = rate * 1.25 + spare
	    cap = guarantee + spare
	ports[pid].tx_cap = cap
	print "Port:   " + ports[pid].port_name
	print "rate ", (rate)
	print "cap  ", (cap)
	tc_tap_change(pid,cap)
        #set_interface_ingress_policing_rate(tap, cap)

def update_flow_caps():
	global ports
	for pid in ports:
		ports[pid].cap_flows()
    


def main():
	global ports
	flows = []
	x = 0
	while True:
	    get_ports()
#	    get_flows()	
	    update_port_caps()
#	    update_flow_caps()
	    for port_id in ports:
		if ports[port_id].port_name == "tapbbb7fbd5-c8":
		    myfile = open('txrate.txt', 'a')
        	    myfile.write("%s %s\n" %(x,ports[port_id].tx_rate))
        	    myfile.close()
	    x = x + 0.1
	    time.sleep(0.1)
	    

if __name__ == '__main__':
    main()
