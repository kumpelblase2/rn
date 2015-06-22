#!/bin/sh
address="172.16.1.0/24"

sudo /usr/sbin/iptables -A INPUT -s $address DROP
sudo /usr/sbin/iptables -t nat -A OUTPUT -d $address DROP
sudo /usr/sbin/iptables -t nat -A PREROUTING -s $address DROP
sudo /usr/sbin/iptables -A OUTPUT -d $address DROP
#sudo /usr/sbin/iptables -A FORWARD -d $address DROP
