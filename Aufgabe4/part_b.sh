address = "172.16.1.0/24"
port = 51000

sudo iptables -A INPUT -s $address DROP
sudo iptables -A OUTPUT -d $address DROP
#sudo iptables -A FORWARD -d $address DROP
sudo iptables -A INPUT -s $address -sport $port -p tcp ALLOW
sudo iptables -A OUTPUT -d $address -dport $port -p tcp ALLOW
#sudo iptables -A FORWARD -d $address -dport $port -p tcp ALLOW
