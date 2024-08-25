#!/bin/bash

# GitHub repository details
GITHUB_USER="aaron777collins"
GITHUB_REPO="ZeroTier-GUI-Arch"
FLATPAK_ID="io.github.aaron777collins.zerotier-gui"
IMAGE_URL="https://github.com/aaron777collins/ZeroTier-GUI-Arch/blob/master/img/zerotier-gui.png?raw=true"


# Install Backend Function
install_backend() {

echo "Downloading zerotier one binary..."
mkdir -p $HOME/.zerotier-one && cd $HOME/.zerotier-one
curl -LJ https://github.com/rafalb8/ZeroTierOne-Static/releases/latest/download/zerotier-one-x86_64.tar.gz \
    | tar --strip-components=1 -xzf -

mkdir -p networks.d
touch networks.d/${Network_ID}.conf

echo "Configuring zerotier one..."

# Binary will be run as a user service, but needs root, so add permission to run sudo without password for zerotier-one
# Tell the user what we will do and that we'll need the sudo password
echo "Adding permission to run zerotier-one without password but you'll need to enter the sudo password:"
# echo "%wheel ALL=(ALL) NOPASSWD: $HOME/.zerotier-one/zerotier-one" | sudo tee /etc/sudoers.d/zerotier 1> /dev/null
# Doing the above command in a konsole window so the user can enter the password

# running the wheel all command with the sudo password
echo "%wheel ALL=(ALL) NOPASSWD: $HOME/.zerotier-one/zerotier-one" | pkexec tee /etc/sudoers.d/zerotier

# Add service file to run at startup
mkdir -p $HOME/.config/systemd/user

# Paste whole command
cat <<EOF > $HOME/.config/systemd/user/zerotier-one.service
[Unit]
After=network.target

[Service]
ExecStart=/usr/bin/sudo %h/.zerotier-one/zerotier-one -U %h/.zerotier-one
Restart=on-failure

[Install]
WantedBy=default.target
EOF
# -----

echo "Starting zerotier one backend..."
systemctl --user daemon-reload
systemctl --user enable --now zerotier-one.service

}

delete_backend() {
  echo "Stopping and disabling ZeroTier One backend..."
  systemctl --user stop zerotier-one.service
  systemctl --user disable zerotier-one.service
  rm -f $HOME/.config/systemd/user/zerotier-one.service
  rm -rf $HOME/.zerotier-one
}

# Function to clean up weird characters
cleanup_console() {
  echo -e "\033[0m" # Reset console formatting
}


# Trap to cleanup console on exit
trap cleanup_console EXIT

echo "Deleting ZeroTier One backend..."
delete_backend

echo "Downloading and installing ZeroTier One backend..."
install_backend

echo "ZeroTier One backend installed successfully!"
exit 0
