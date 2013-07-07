#!/bin/bash
#To copy the isa_id into a remote server 
# test "tc qdisc show dev $1 | wc -l" -gt 1 && (echo "tc qdisc show dev $1 | wc -l"; tc qdisc del dev $1 root)
QDISC= tc qdisc show dev $1 | wc -l
#test "$QDISC" -gt "1" && tc qdisc del dev $1 root
 tc qdisc add dev $1 root handle 1: htb default 30
#The total outgoing bandwidth : 1000mbit:
#The bandwidth for each vNic
 tc class add dev $1 parent 1:0 classid 1:6 htb rate 600mbit
 tc class add dev $1 parent 1:0 classid 1:8 htb rate 200mbit
 tc class add dev $1 parent 1:0 classid 1:30 htb rate 10kbit
#The bandwidth for vNIC one :
 tc class add dev $1 parent 1:6 classid 1:618 htb rate 500mbit
 tc class add dev $1 parent 1:6 classid 1:699 htb rate 100mbit 

echo "class done"
 tc qdisc add dev $1 parent 1:6 handle 6: sfq perturb 10
 tc qdisc add dev $1 parent 1:8 handle 8: sfq perturb 10
 tc qdisc add dev $1 parent 1:30 handle 30: sfq perturb 10
 tc qdisc add dev $1 parent 1:618 handle 618: sfq perturb 10
 tc qdisc add dev $1 parent 1:699 handle 699: sfq perturb 10

echo "filter done"
 U32="tc filter add dev $1 protocol ip parent 1:0 prio 1 u32"
tc filter add dev $1 protocol ip parent 1:0 prio 1 u32 match ip dst 192.168.1.18 flowid 1:618
tc filter add dev $1 protocol ip parent 1:0 prio 2 u32 match ip dst 192.168.2.0/24 flowid 1:8
tc filter add dev $1 protocol ip parent 1:0 prio 2 u32 match ip dst 192.168.1.0/24 flowid 1:699
