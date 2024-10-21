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
  
  echo "Removing ZeroTier One backend files..."
  rm -rf $HOME/.zerotier-one
  rm $HOME/.config/systemd/user/zerotier-one.service
  
  echo "Removing sudo permission for ZeroTier One..."
  sudo rm /etc/sudoers.d/zerotier
  
  echo "Backend uninstalled successfully."
}

# Function to clean up weird characters
cleanup_console() {
  echo -e "\033[0m" # Reset console formatting
}

# Trap to cleanup console on exit
trap cleanup_console EXIT

# Ask user if they want to uninstall the ZeroTier One backend
uninstall_backend_prompt=$(zenity --question --title="Uninstall ZeroTier One Backend" --text="Do you want to uninstall the ZeroTier One backend?" --ok-label="Yes" --cancel-label="No"; echo $?)

if [ "$uninstall_backend_prompt" -eq 0 ]; then
  if [ -f "$HOME/.zerotier-one/zerotier-one" ]; then
    echo "Uninstalling ZeroTier One backend..."
    uninstall_backend
  else
    echo "ZeroTier One backend is not installed."
  fi
else
  echo "Skipping ZeroTier One backend uninstallation."
fi

# Checking if Flatpak is installed
if ! command -v flatpak &> /dev/null; then
  echo "Flatpak is not installed, skipping Flatpak-related uninstallation."
  exit 0
fi

# Uninstall the Flatpak package
echo "Uninstalling the Flatpak package..."
flatpak uninstall --user --assumeyes $FLATPAK_ID

if [ $? -ne 0 ]; then
  echo "Error: Failed to uninstall the Flatpak package."
else
  echo "Flatpak package uninstalled successfully."
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
