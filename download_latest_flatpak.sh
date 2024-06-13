#!/bin/bash

# GitHub repository details
GITHUB_USER="aaron777collins"
GITHUB_REPO="ZeroTier-GUI-Arch"
FLATPAK_ID="io.github.aaron777collins.zerotier-gui"

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

# Ensure the necessary directories exist
echo "Ensuring necessary directories exist..."
mkdir -p /var/lib/flatpak/exports/share
mkdir -p /home/$USER/.local/share/flatpak/exports/share

# Install the necessary runtime
echo "Installing the necessary runtime..."
flatpak install -y flathub org.freedesktop.Platform//22.08

if [ $? -ne 0 ]; then
  echo "Error: Failed to install the necessary runtime."
  exit 1
fi

# Install the Flatpak package
echo "Installing the Flatpak package..."
flatpak install --user --assumeyes zerotier-gui.flatpak

if [ $? -ne 0 ]; then
  echo "Error: Failed to install the Flatpak package."
  exit 1
fi

echo "Successfully installed the Flatpak package."

# Run the Flatpak application
echo "Launching the Flatpak application..."
flatpak run $FLATPAK_ID

if [ $? -ne 0 ]; then
  echo "Error: Failed to launch the Flatpak application."
  exit 1
fi

echo "Flatpak application launched successfully."
