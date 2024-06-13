#!/bin/bash

# GitHub repository details
GITHUB_USER="aaron777collins"
GITHUB_REPO="ZeroTier-GUI-Arch"

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
