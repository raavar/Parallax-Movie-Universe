#!/bin/bash

echo "--- CONFIGURING FIREWALL ---"

# Remove all existing firewall rules to ensure a clean slate and prevent conflicts
sudo iptables -F

# Allow incoming SSH connections on port 22 to ensure remote access is maintained
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow internal traffic on Docker network bridges so containers can communicate with each other
sudo iptables -I INPUT -i br+ -j ACCEPT
sudo iptables -I FORWARD -i br+ -j ACCEPT
sudo iptables -I FORWARD -o br+ -j ACCEPT

# Allow incoming HTTP and HTTPS traffic on ports 80 and 443 for the web server
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

# Allow traffic on the loopback interface for internal system communication
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow incoming traffic for connections that are already established or related to outgoing requests
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Save the current iptables rules to ensure they persist after a reboot
sudo netfilter-persistent save

# Restart the Docker service to ensure network bridges are correctly applied with the new firewall rules
echo "Restarting Docker service..."
sudo systemctl restart docker

echo "--- FIREWALL CONFIGURED ---"