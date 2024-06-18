#!/bin/bash

# Install necessary dependencies
sudo pacman -Syu --noconfirm flatpak flatpak-builder gcc make

# Ensure the Flathub repository is added
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install GNOME SDK and Platform
flatpak install -y flathub org.gnome.Platform/x86_64/46 org.gnome.Sdk/x86_64/46

# Build the Flatpak
flatpak-builder --user --install --force-clean build-dir io.github.aaron777collins.zerotier-gui.yml

# Export the repository
flatpak build-export repo build-dir

# Bundle the Flatpak package
flatpak build-bundle repo zerotier-gui.flatpak io.github.aaron777collins.zerotier-gui

# Notify the user of completion
echo "Build and bundle complete. The Flatpak package is available as zerotier-gui.flatpak."
