#!/bin/sh
address="172.16.1.0/24"
port=51000

sudo /usr/sbin/iptables -A INPUT -s $address -j DROP
sudo /usr/sbin/iptables -A OUTPUT -d $address -j DROP
#sudo /usr/sbin/iptables -A FORWARD -d $address -j DROP
sudo /usr/sbin/iptables -A INPUT -s $address -sport $port -p tcp -j ALLOW
sudo /usr/sbin/iptables -A OUTPUT -d $address -dport $port -p tcp -j ALLOW
#sudo /usr/sbin/iptables -A FORWARD -d $address -dport $port -p tcp -j ALLOW
