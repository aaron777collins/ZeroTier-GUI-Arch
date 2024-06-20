# ZeroTier-GUI Arch <img src="img/zerotier-gui.png" align="bottom">

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square)](https://github.com/tralph3/ZeroTier-GUI/blob/master/LICENSE)

**A Linux front-end for ZeroTier**

### Manage Networks
<img src="img/managenetworks1.png " width="1000">
<img src="img/managenetworks2.png " width="1000">

### Manage Peers
<img src="img/managepeers.png " width="1000">

# DOWNLOAD INSTALLER HERE
<a href="https://github.com/aaron777collins/ZeroTier-GUI-Arch/releases/latest/download/install_zerotier_gui.desktop" download>
    <img src="https://github.com/aaron777collins/ZeroTier-GUI-Arch/blob/master/img/Download.png?raw=true" alt="Install ZeroTier GUI">
</a>

> Drag the downloaded file to the desktop, run it, and follow the instructions. This will install the ZeroTier-One backend and the ZeroTier-GUI frontend. **If you want to use the frontend in Steam-OS' game-mode, you'll need to right click the ZeroTier GUI icon generated on the desktop and select `Add To Steam`**

# Installation Frontend (Flatpak) + Backend
You can use the installer file above by downloading it, dragging it onto your desktop and running that. Otherwise, you can follow the instructions below using Konsole or your preferred terminal. Note: The installation script assumes konsole and zenity will be installed on the user's system. If you're using a different terminal or don't have zenity, you may need to modify the script.

1. **Install Flatpak:**
Follow the instructions on the [Flatpak website](https://flatpak.org/setup/) to install Flatpak for your distribution if it isn't already installed. For Steam Deck, it should already be installed. You can skip this step if you're on Steam Deck.
2. **Download & Install the Flatpak package:**
   Run the following command to download the latest release:
   ```bash
   curl -s https://raw.githubusercontent.com/aaron777collins/ZeroTier-GUI-Arch/master/download_and_install_zerotier_one.sh | bash
   ```

> *Note:* This installation script uses work from sebbi08's ZeroTierOne-Static [Installation Instructions/Script](https://github.com/rafalb8/ZeroTierOne-Static/blob/main/SteamDeck.md). For the frontend, I modified [tralph3's ZeroTier-GUI](https://github.com/tralph3/ZeroTier-GUI) repository to work with flatpak and the static backend.

# Installation (Source)
1. **Clone the repository:**

   ```bash
   git clone https://github.com/aaron777collins/zerotier-gui.git
   cd zerotier-gui
   ```
2. **Install dependencies**

   This depends on your platform. For Arch, you may need to run

   ```bash
   sudo pacman -S tk
   ```
3. **Run the application (Not Flatpak)**

   ```bash
   python src/zerotier-gui.py
    ```

# Usage

## Launching the Application
```bash
flatpak run io.github.aaron777collins.zerotier-gui
```

After launching the application, you can use the graphical interface to manage your ZeroTier networks and peers.

## Manage Networks
* **Refresh Networks:** Refresh the list of joined networks.
* **Join Network:** Join a new ZeroTier network by entering the network ID.
* **Leave Network:** Leave a selected network.
* **Network Info:** View detailed information about a selected network.
* **Toggle Interface Connection:** Disconnect or connect the network interface.
* **ZeroTier Central:** Open ZeroTier Central in your default web browser.

## Manage Peers
* **Show Peers:** View the list of peers in the network.
* **Refresh Peers:** Refresh the list of peers.
* **See Paths:** View the paths for a selected peer.

# Dependencies

None of the packages contains the back-end, zerotier-one. Arch has it in the `community` repo. For Ubuntu based distributions, you'll need to install it manually [from their website](https://www.zerotier.com/download/). On top of that, you'll need python3.6 or greater, and the tkinter module. This however should be handled by the packaging software. Service management depends on SystemD. You will **not** be able to enable or disable the ZeroTier service without it.
