#1/bin/sh
address="172.16.1.0/24"

sudo /usr/sbin/iptables -A INPUT -s $address -p tcp DROP
sudo /usr/sbin/iptables -A OUTPUT -d $address -p tcp DROP
#sudo /usr/sbin/iptables -A FORWARD -d $address -p tcp DROP
