#!/bin/bash

echo "--- CONFIGURING FIREWALL ---"

# 1. Flush existing rules to prevent conflicts/duplicates
sudo iptables -F

# 2. Allow SSH (CRITICAL: Prevents locking yourself out)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 3. Allow Internal Docker Traffic (Fixes 'Connection Timed Out' between Web and DB)
sudo iptables -I INPUT -i br+ -j ACCEPT
sudo iptables -I FORWARD -i br+ -j ACCEPT
sudo iptables -I FORWARD -o br+ -j ACCEPT

# 4. Allow Public Web Traffic (Caddy/HTTPS)
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

# 5. Allow Loopback (Internal system talk)
sudo iptables -A INPUT -i lo -j ACCEPT

# 6. Allow Established Connections (So the server can reply to you)
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# 7. Save rules
sudo netfilter-persistent save

# 8. Restart Docker to apply network bridges
echo "Restarting Docker service..."
sudo systemctl restart docker

echo "--- FIREWALL CONFIGURED ---"