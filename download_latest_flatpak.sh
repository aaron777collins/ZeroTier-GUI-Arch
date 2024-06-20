#!/bin/bash

# GitHub repository details
GITHUB_USER="aaron777collins"
GITHUB_REPO="ZeroTier-GUI-Arch"
FLATPAK_ID="io.github.aaron777collins.zerotier-gui"

# Function to clean up weird characters
cleanup_console() {
  echo -e "\033[0m" # Reset console formatting
  if [ -t 1 ]; then
    stty sane # Restore terminal settings only if in an interactive terminal
  fi
}


# Trap to cleanup console on exit
trap cleanup_console EXIT

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

# Create/update the desktop file
DESKTOP_FILE="$HOME/Desktop/ZeroTier-GUI.desktop"
echo "Creating/updating the desktop file at $DESKTOP_FILE..."
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Encoding=UTF-8
Exec=sh -c 'unset LD_PRELOAD && flatpak run io.github.aaron777collins.zerotier-gui'
Icon=zerotier-gui
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
