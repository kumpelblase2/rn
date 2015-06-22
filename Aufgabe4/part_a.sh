address = "172.16.1.0/24"

sudo iptables -A INPUT -s $address DROP
sudo iptables -t nat -A OUTPUT -d $address DROP
sudo iptables -t nat -A PREROUTING -s $address DROP
sudo iptables -A OUTPUT -d $address DROP
#sudo iptables -A FORWARD -d $address DROP
