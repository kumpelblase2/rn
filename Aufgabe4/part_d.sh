address = "172.16.1.0/24"

sudo iptables -A INPUT -s $address -p icmp DROP
sudo iptables -A OUTPUT -d $address -p icmp ALLOW
sudo iptables -A FORWARD -d $address -p icmpALLOW
