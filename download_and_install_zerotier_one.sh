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

# Open a new konsole window to run the command
konsole -e "echo \"%wheel ALL=(ALL) NOPASSWD: $HOME/.zerotier-one/zerotier-one\" | sudo tee /etc/sudoers.d/zerotier 1> /dev/null"
# Using zenity to ask the user if the sudo password used
sudo_password_used=$(zenity --question --title="Sudo Password Used" --text="Did you enter the sudo password when prompted?" --ok-label="Yes" --cancel-label="No"; echo $?)
if [ "$sudo_password_used" -ne 0 ]; then
  echo "Error: Sudo password not entered. Exiting..."
  # Tell the user in a gui that they need to enter the sudo password themselves using the terminal command 'passwd' and then try the installation again
  zenity --error --title="Sudo Password Not Entered" --text="Please enter the sudo password when prompted and then try the installation again." --no-wrap
  exit 1
else
  echo "Selected: Sudo password entered."
fi

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

# Function to clean up weird characters
cleanup_console() {
  echo -e "\033[0m" # Reset console formatting
}


# Trap to cleanup console on exit
trap cleanup_console EXIT

# Ask the user if they need to set the sudo password or if it is already setup
set_sudo_password=$(zenity --question --title="Sudo Password Setup" --text="Do you need to set the sudo password for the user to run zerotier-one?" --ok-label="Yes" --cancel-label="No"; echo $?)

if [ "$set_sudo_password" -eq 0 ]; then
  echo "Opening Konsole to set the sudo password..."
  konsole -e "passwd"
  # Using zenity to ask the user if the sudo password was set
  sudo_password_set=$(zenity --question --title="Sudo Password Setup" --text="Was the sudo password set successfully?" --ok-label="Yes" --cancel-label="No"; echo $?)
  if [ "$sudo_password_set" -ne 0 ]; then
    echo "Error: Sudo password not set. Exiting..."
    # Tell the user in a gui that they need to set the sudo password themselves using passwd and then try the installation again
    zenity --error --title="Sudo Password Not Set" --text="Please set the sudo password using the terminal command 'passwd' and then try the installation again." --no-wrap
    exit 1
  else
    echo "Selected: Sudo password set successfully."
  fi
else
  echo "Selected: Sudo password already set."
fi

# Installing the zero tier one backend

# Check if the zero tier one backend is already installed
if [ -f "$HOME/.zerotier-one/zerotier-one" ]; then
  echo "ZeroTier One backend is already installed."
else
  echo "ZeroTier One backend is not installed. Installing..."
  install_backend
fi

# Checking if flatpak is installed yet
# If not, tell the user to install it
if ! command -v flatpak &> /dev/null; then
  echo "Error: Flatpak is not installed. Please install Flatpak and try again. You can install Flatpak using your package manager or go to https://www.flatpak.org/setup/ for more information. Exiting..."
  exit 1
fi

# Fetch the latest release information from GitHub API
echo "Fetching the latest release information from GitHub..."
release_info=$(curl -s "https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/releases/latest")

# Extract the download URL for the Flatpak package
flatpak_url=$(echo "$release_info" | grep -E 'browser_download_url.*zerotier-gui\.flatpak' | cut -d '"' -f 4)

if [ -z "$flatpak_url" ]; then
  echo "Error: Unable to find the download URL for the Flatpak package."
  exit 1
fi

echo "Download URL found: $flatpak_url"

# Download the Flatpak package
echo "Downloading the latest Flatpak package..."
curl -L -o zerotier-gui.flatpak "$flatpak_url"

if [ $? -ne 0 ]; then
  echo "Error: Failed to download the Flatpak package."
  exit 1
fi

echo "Successfully downloaded the latest Flatpak package: zerotier-gui.flatpak"

# Ensure the necessary user-level directories exist
echo "Ensuring necessary user-level directories exist..."
mkdir -p "$HOME/.local/share/flatpak/exports/share"

# Add the Flathub remote for the user if not already added
echo "Adding Flathub remote if not already added..."
flatpak --user remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install the necessary runtime at the user level
echo "Installing the necessary runtime..."
flatpak install --user -y flathub org.gnome.Platform/x86_64/46 2>&1 | tee /dev/null

if [ $? -ne 0 ]; then
  echo "Error: Failed to install the necessary runtime."
  exit 1
fi

# Install the Flatpak package from the downloaded file
echo "Installing the Flatpak package..."
flatpak install --user --assumeyes ./zerotier-gui.flatpak 2>&1 | tee /dev/null

if [ $? -ne 0 ]; then
  echo "Error: Failed to install the Flatpak package."
  exit 1
fi

echo "Successfully installed the Flatpak package."

# Get the version from the VERSION file
if [ -f VERSION ]; then
  VERSION=$(cat VERSION)
else
  VERSION="0.0.82"
fi

# Download the icon image for the desktop entry
echo "Downloading the icon image for the desktop entry..."
curl -L -o "$HOME/.local/share/icons/zerotier-gui.png" "$IMAGE_URL"

if [ $? -ne 0 ]; then
  echo "Error: Failed to download the icon image."
  exit 1
fi

echo "Successfully downloaded the icon image."

# Create/update the desktop file
DESKTOP_FILE="$HOME/Desktop/ZeroTier-GUI.desktop"
echo "Creating/updating the desktop file at $DESKTOP_FILE..."
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Encoding=UTF-8
Exec=sh -c 'unset LD_PRELOAD && flatpak run io.github.aaron777collins.zerotier-gui'
Icon=$HOME/.local/share/icons/zerotier-gui.png
Type=Application
Terminal=false
Comment=Linux front-end for ZeroTier
Name=ZeroTier GUI
GenericName=ZeroTier GUI
StartupWMClass=zerotier-gui
StartupNotify=false
Categories=Utility;
Version=$VERSION
EOF

# Ensure the desktop file is executable
chmod +x "$DESKTOP_FILE"

echo "Desktop file created/updated successfully at $DESKTOP_FILE."

# Final cleanup
cleanup_console
echo "Script completed successfully."
