#!/bin/sh
address="172.16.1.0/24"

sudo /usr/sbin/iptables -A INPUT -s $address -p icmp -j DROP
sudo /usr/sbin/iptables -A OUTPUT -d $address -p icmp -j ALLOW
sudo /usr/sbin/iptables -A FORWARD -d $address -p icmp -j ALLOW
