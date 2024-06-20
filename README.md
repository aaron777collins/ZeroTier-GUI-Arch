# ZeroTier-GUI Arch <img src="img/zerotier-gui.png" align="bottom">

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square)](https://github.com/tralph3/ZeroTier-GUI/blob/master/LICENSE)

**A Linux front-end for ZeroTier**

### Manage Networks
<img src="img/managenetworks1.png " width="1000">
<img src="img/managenetworks2.png " width="1000">

### Manage Peers
<img src="img/managepeers.png " width="1000">

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

# Installation (Flatpak)
1. **Install Flatpak:**
Follow the instructions on the [Flatpak website](https://flatpak.org/setup/) to install Flatpak for your distribution if it isn't already installed. For Steam Deck, it should already be installed. You can skip this step if you're on Steam Deck.
2. **Download & Install the Flatpak package:**
   Run the following command to download the latest release:
   ```bash
   curl -s https://raw.githubusercontent.com/aaron777collins/ZeroTier-GUI-Arch/master/download_and_install_zerotier_one.sh | bash
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
