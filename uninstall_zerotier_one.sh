#!/bin/bash

# GitHub repository details
GITHUB_USER="aaron777collins"
GITHUB_REPO="ZeroTier-GUI-Arch"
FLATPAK_ID="io.github.aaron777collins.zerotier-gui"

# Uninstall Backend Function
uninstall_backend() {
  echo "Stopping ZeroTier One backend service..."
  systemctl --user stop zerotier-one.service
  systemctl --user disable zerotier-one.service
  
  echo "Removing ZeroTier One backend files and peer files..."
  
  # Group all privileged remove commands into a single pkexec call
  pkexec bash -c "
    rm -rf '$HOME/.zerotier-one';
    rm '$HOME/.config/systemd/user/zerotier-one.service';
    rm /etc/sudoers.d/zerotier
  "

  if [ $? -eq 0 ]; then
    echo "Backend uninstalled and peer files removed successfully."
  else
    echo "Error: Failed to uninstall backend or remove peer files."
  fi
}

# Function to clean up weird characters
cleanup_console() {
  echo -e "\033[0m" # Reset console formatting
}

# Trap to cleanup console on exit
trap cleanup_console EXIT

# Check if ZeroTier One is installed
if [ -f "$HOME/.zerotier-one/zerotier-one" ]; then
  echo "Uninstalling ZeroTier One backend and cleaning peer files..."
  uninstall_backend
else
  echo "ZeroTier One backend is not installed."
fi

# Checking if Flatpak is installed
if ! command -v flatpak &> /dev/null; then
  echo "Flatpak is not installed, skipping Flatpak-related uninstallation."
else
  # Run flatpak uninstall in the background using nohup
  echo "Uninstalling the Flatpak package in the background..."
  nohup bash -c "flatpak uninstall --user --assumeyes $FLATPAK_ID" > /dev/null 2>&1 &
  echo "Flatpak uninstallation running in the background."
fi

# Removing desktop file and icon
DESKTOP_FILE="$HOME/Desktop/ZeroTier-GUI.desktop"
if [ -f "$DESKTOP_FILE" ]; then
  echo "Removing desktop file..."
  rm "$DESKTOP_FILE"
else
  echo "Desktop file not found, skipping."
fi

ICON_FILE="$HOME/.local/share/icons/zerotier-gui.png"
if [ -f "$ICON_FILE" ]; then
  echo "Removing icon image..."
  rm "$ICON_FILE"
else
  echo "Icon image not found, skipping."
fi

# Final cleanup
cleanup_console
echo "Uninstall script completed successfully."
