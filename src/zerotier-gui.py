#!/usr/bin/env python3
#
# A Linux front-end for ZeroTier
# Copyright (C) 2023 Tomás Ralph
# Copyright (C) 2024 Aaron Collins
# Original Author: Tomás Ralph
# Upgraded and packaged by Aaron Collins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Modifications:
# - Added exit button that saves (useful in Steam-OS game-mode)
# - Adjusted about screen
# - Remapped functions to work within a flatpak
# - Remapped functions to work with a static version of ZeroTier
# - Changed some of the functions to work in a more generic sense (getting the username)
# - Asking the user for their password to run commands as root
# - Cleaning up the code to be more uniform in the way it runs commands
# - This is outside this file but I added a release pipeline and install script to make it really easy to install
# - the backend for zerotier-one (rafalb8's ZeroTierOne-Static).
# - Link to the static version of ZeroTierOne-Static that is used: https://github.com/rafalb8/ZeroTierOne-Static/tree/main
#
######################################
#                                    #
# Originally created by tralph3      #
#   https://github.com/tralph3       #
#    Modified + Packaged By          #
#         aaron777collins            #
# https://github.com/aaron777collins #
#                                    #
######################################

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from subprocess import PIPE, Popen, check_output, STDOUT, CalledProcessError
import json
from json import JSONDecodeError
from os import getuid, system, _exit, path, makedirs
from webbrowser import open_new
from tkinter import simpledialog
import sys
from datetime import datetime
import textwrap
import os
import pwd

BACKGROUND = "#d9d9d9"
FOREGROUND = "black"
BUTTON_BACKGROUND = "#ffb253"
BUTTON_ACTIVE_BACKGROUND = "#ffbf71"

HISTORY_FILE_DIRECTORY = path.expanduser("~/.local/share/zerotier-gui")
HISTORY_FILE_NAME = "network_history.json"

DEBUG_MODE = False


class MainWindow:
    def __init__(self):
        self.load_network_history()

        self.window = tk.Tk(className="zerotier-gui")
        self.window.title("ZeroTier-GUI")
        self.window.resizable(width=False, height=False)

        # layout setup
        self.topFrame = tk.Frame(self.window, padx=20, pady=10, bg=BACKGROUND)
        self.topBottomFrame = tk.Frame(self.window, padx=20, bg=BACKGROUND)
        self.middleFrame = tk.Frame(self.window, padx=20, bg=BACKGROUND)
        self.bottomFrame = tk.Frame(
            self.window, padx=20, pady=10, bg=BACKGROUND
        )

        # widgets
        self.networkLabel = tk.Label(
            self.topFrame,
            text="Joined Networks:",
            font=40,
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        self.refreshButton = self.formatted_buttons(
            self.topFrame,
            text="Refresh Networks",
            command=self.refresh_networks,
        )
        self.aboutButton = self.formatted_buttons(
            self.topFrame, text="About", command=self.about_window
        )
        self.peersButton = self.formatted_buttons(
            self.topFrame, text="Show Peers", command=self.see_peers
        )
        self.joinButton = self.formatted_buttons(
            self.topFrame,
            text="Join Network",
            command=self.create_join_network_window,
        )

        self.networkListScrollbar = tk.Scrollbar(
            self.middleFrame, bd=2, bg=BACKGROUND
        )

        self.networkList = TreeView(
            self.middleFrame, "Network ID", "Name", "Status"
        )
        self.networkList.column("Network ID", width=40)
        self.networkList.column("Status", width=40)

        self.networkList.bind("<Double-Button-1>", self.call_see_network_info)

        self.leaveButton = self.formatted_buttons(
            self.bottomFrame,
            text="Leave Network",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=self.leave_network,
        )
        self.ztCentralButton = self.formatted_buttons(
            self.bottomFrame,
            text="ZeroTier Central",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=self.zt_central,
        )
        self.toggleConnectionButton = self.formatted_buttons(
            self.bottomFrame,
            text="Disconnect/Connect Interface",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=self.toggle_interface_connection,
        )
        self.toggleServiceButton = self.formatted_buttons(
            self.bottomFrame,
            text="Toggle ZT Service",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=self.toggle_service,
        )
        self.serviceStatusLabel = tk.Label(
            self.bottomFrame, font=40, bg=BACKGROUND, fg=FOREGROUND
        )
        self.infoButton = self.formatted_buttons(
            self.bottomFrame,
            text="Network Info",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=self.see_network_info,
        )

        self.exitButton = self.formatted_buttons(
            self.bottomFrame,
            text="Exit",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=self.on_exit,
        )

        # pack widgets
        self.networkLabel.pack(side="left", anchor="sw")
        self.refreshButton.pack(side="right", anchor="se")
        self.aboutButton.pack(side="right", anchor="sw")
        self.peersButton.pack(side="right", anchor="sw")
        self.joinButton.pack(side="right", anchor="se")

        self.networkListScrollbar.pack(side="right", fill="both")
        self.networkList.pack(side="bottom", fill="x")

        self.leaveButton.pack(side="left", fill="x")
        self.toggleConnectionButton.pack(side="left", fill="x")
        self.exitButton.pack(side="right", fill="x")
        self.infoButton.pack(side="right", fill="x")
        self.ztCentralButton.pack(side="right", fill="x")
        self.toggleServiceButton.pack(side="right", fill="x")
        self.serviceStatusLabel.pack(side="right", fill="x", padx=(100, 0))

        # frames
        self.topFrame.pack(side="top", fill="x")
        self.topBottomFrame.pack(side="top", fill="x")
        self.middleFrame.pack(side="top", fill="x")
        self.bottomFrame.pack(side="top", fill="x")

        # extra configuration
        self.refresh_networks()
        self.update_service_label()

        self.networkList.config(yscrollcommand=self.networkListScrollbar.set)
        self.networkListScrollbar.config(command=self.networkList.yview)

    def open_new_window(self, url: str) -> None:
        # Check if you are running SteamOS using lsbrelease
        res = run_command(["lsb_release", "-d"])
        sres = res.strip()
        if "SteamOS" in sres:
            # If you are running SteamOS, open the link in the Steam Browser
            run_command(["steam", "steam://openurl/" + url], use_sudo=False)
        else:
            open_new(url)

    def load_network_history(self):
        history_file_path = path.join(
            HISTORY_FILE_DIRECTORY, HISTORY_FILE_NAME
        )
        if not path.isfile(history_file_path):
            makedirs(HISTORY_FILE_DIRECTORY, exist_ok=True)
            with open(history_file_path, "w") as f:
                pass
        with open(history_file_path, "r") as f:
            try:
                self.network_history = json.load(f)
            except JSONDecodeError:
                self.network_history = {}

    def toggle_service(self):
        state = self.get_service_status()
        if state == "active":
            manage_service("stop")
        else:
            manage_service("start")
        self.update_service_label()

    def get_service_status(self):
        data = manage_service("show").split("\n")
        formatted_data = {}
        for entry in data:
            key_value = entry.split("=", 1)
            if len(key_value) == 2:
                formatted_data[key_value[0]] = key_value[1]

        return formatted_data["ActiveState"]

    def update_service_label(self):
        state = self.get_service_status()
        self.serviceStatusLabel.configure(text=f"Service Status: {state} | ")

    def zt_central(self):
        self.open_new_window("https://my.zerotier.com/network")

    def call_see_network_info(self, event):
        self.see_network_info()

    def refresh_paths(self, pathsList, idInList):
        pathsList.delete(*pathsList.get_children())
        paths = []
        # outputs info of paths in json format
        pathsData = self.get_peers_info()[idInList]["paths"]

        # get paths information in a list of tuples
        for pathPosition in range(len(pathsData)):
            paths.append(
                (
                    pathsData[pathPosition]["active"],
                    pathsData[pathPosition]["address"],
                    pathsData[pathPosition]["expired"],
                    pathsData[pathPosition]["lastReceive"],
                    pathsData[pathPosition]["lastSend"],
                    pathsData[pathPosition]["preferred"],
                    pathsData[pathPosition]["trustedPathId"],
                )
            )

        # set paths in listbox
        for (
            pathActive,
            pathAddress,
            pathExpired,
            pathLastReceive,
            pathLastSend,
            pathPreferred,
            pathTrustedId,
        ) in paths:
            pathsList.insert(
                (
                    str(pathActive),
                    str(pathAddress),
                    str(pathExpired),
                    str(pathLastReceive),
                    str(pathLastSend),
                    str(pathPreferred),
                    str(pathTrustedId),
                )
            )

    def refresh_peers(self, peersList):
        peersList.delete(*peersList.get_children())
        peers = []
        # outputs info of peers in json format
        peersData = self.get_peers_info()

        # get peers information in a list of tuples
        for peerPosition in range(len(peersData)):
            peers.append(
                (
                    peersData[peerPosition]["address"],
                    peersData[peerPosition]["version"],
                    peersData[peerPosition]["role"],
                    peersData[peerPosition]["latency"],
                )
            )

        # set peers in listbox
        for peerAddress, peerVersion, peerRole, peerLatency in peers:
            if peerVersion == "-1.-1.-1":
                peerVersion = "-"
            peersList.insert((peerAddress, peerVersion, peerRole, peerLatency))

    def refresh_networks(self):
        self.networkList.delete(*self.networkList.get_children())
        networks = []
        # outputs info of networks in json format
        networkData = self.get_networks_info()

        # gets networks information in a list of tuples
        for networkPosition in range(len(networkData)):
            interfaceState = self.get_interface_state(
                networkData[networkPosition]["portDeviceName"]
            )
            isDown = interfaceState.lower() == "down"
            networks.append(
                (
                    networkData[networkPosition]["id"],
                    networkData[networkPosition]["name"],
                    networkData[networkPosition]["status"],
                    isDown,
                )
            )
        # set networks in listbox
        for (
            networkId,
            networkName,
            networkStatus,
            isDown,
        ) in networks:
            if not networkName:
                networkName = "Unknown Name"
            self.networkList.insert(
                (networkId, networkName, networkStatus), isDown
            )

        self.update_network_history_names()

    def update_network_history_names(self):
        networks = self.get_networks_info()
        for network in networks:
            network_id = network["nwid"]
            network_name = network["name"]
            if network_id in self.network_history:
                self.network_history[network_id]["name"] = network_name

    def save_network_history(self):
        history_file_path = path.join(
            HISTORY_FILE_DIRECTORY, HISTORY_FILE_NAME
        )
        with open(history_file_path, "w") as f:
            json.dump(self.network_history, f)

    def get_network_name_by_id(self, network_id):
        networks = self.get_networks_info()
        for network in networks:
            if network_id == network["nwid"]:
                return network["name"]

    def get_networks_info(self):
        res = run_zerotier_cli("-j", "listnetworks")
        # print(res)
        resj = json.loads(res)
        # print(resj)
        return resj

    def get_peers_info(self):
        return json.loads(run_zerotier_cli("-j", "peers"))

    def launch_sub_window(self, title):
        subWindow = tk.Toplevel(self.window, class_="zerotier-gui")
        subWindow.title(title)
        subWindow.resizable(width=False, height=False)

        return subWindow

    # creates entry widgets to select and copy text
    def selectable_text(
        self, frame, text, justify="left", font="TkDefaultFont"
    ):
        entry = tk.Entry(
            frame,
            relief=tk.FLAT,
            bg=BACKGROUND,
            highlightthickness=0,
            highlightcolor=BACKGROUND,
            fg=FOREGROUND,
            selectforeground=FOREGROUND,
            selectborderwidth=0,
            justify=justify,
            font=font,
            bd=0,
        )
        entry.insert(0, text)
        entry.config(state="readonly", width=len(text))

        return entry

    # creates correctly formatted buttons
    def formatted_buttons(
        self,
        frame,
        text="",
        bg=BUTTON_BACKGROUND,
        fg=FOREGROUND,
        justify="left",
        activebackground=BUTTON_ACTIVE_BACKGROUND,
        command="",
        activeforeground=FOREGROUND,
    ):
        button = tk.Button(
            frame,
            text=text,
            bg=bg,
            fg=fg,
            justify=justify,
            activebackground=activebackground,
            activeforeground=activeforeground,
            command=command,
        )
        return button

    def add_network_to_history(self, network_id):
        network_name = self.get_network_name_by_id(network_id)
        date = datetime.now()
        join_date = f"{date.year}/{date.month:0>2}/{date.day:0>2} {date.hour:0>2}:{date.minute:0>2}"
        self.network_history[network_id] = {
            "name": network_name,
            "join_date": join_date,
        }

    def is_on_network(self, network_id):
        currently_joined = False
        for network in self.get_networks_info():
            if currently_joined:
                break
            currently_joined = network["nwid"] == network_id
        return currently_joined

    def create_join_network_window(self):
        def join_network(network_id):
            try:
                if self.is_on_network(network_id):
                    join_result = "You're already a member of this network."
                    messagebox.showinfo(
                        icon="info", message=join_result, parent=join_window
                    )
                    return
                run_zerotier_cli("join", network_id)
                join_result = "Successfully joined network"
                self.add_network_to_history(network_id)
                messagebox.showinfo(
                    icon="info", message=join_result, parent=join_window
                )
                self.refresh_networks()
                join_window.destroy()
            except CalledProcessError:
                join_result = "Invalid network ID"
                messagebox.showinfo(
                    icon="error", message=join_result, parent=join_window
                )

        def populate_network_list():
            network_history_list.delete(*network_history_list.get_children())
            for network_id in self.network_history:
                network_name = self.network_history[network_id]["name"]
                if network_name == "":
                    network_name = "Unknown Name"
                network_history_list.insert((network_name, network_id))

        def populate_info_sidebar():
            selected_item = network_history_list.focus()
            if selected_item != "":
                item_info = network_history_list.item(selected_item)["values"]
                network_id = item_info[1]
                join_date = self.network_history[network_id]["join_date"]
                network_name = self.network_history[network_id]["name"]
                if network_name == "":
                    network_name = "Unknown Name"
                currently_joined = self.is_on_network(network_id)
            else:
                network_id = "-"
                join_date = "-"
                currently_joined = "-"
                network_name = "-"
            network_id_label.configure(
                text="{:20s}{}".format("Network ID:", network_id)
            )
            network_name_label.configure(
                text="{:20s}{}".format("Name:", network_name)
            )
            last_joined_label.configure(
                text="{:20s}{}".format("Last joined date:", join_date)
            )
            currently_joined_label.configure(
                text="{:20s}{}".format("Currently joined:", currently_joined)
            )

        def on_network_selected(event):
            populate_info_sidebar()
            selected_item = network_history_list.focus()
            item_info = network_history_list.item(selected_item)["values"]
            network_id = item_info[1]
            network_entry_value.set(network_id)

        def delete_history_entry():
            selected_item = network_history_list.focus()
            item_info = network_history_list.item(selected_item)["values"]
            network_id = item_info[1]
            self.network_history.pop(network_id)
            populate_network_list()

        join_window = self.launch_sub_window("Join Network")
        join_window.configure(bg=BACKGROUND)

        network_entry_value = tk.StringVar()

        main_frame = tk.Frame(join_window, padx=20, pady=20, bg=BACKGROUND)
        middle_frame = tk.Frame(main_frame, bg=BACKGROUND)
        left_frame = tk.LabelFrame(
            middle_frame, bg=BACKGROUND, fg=FOREGROUND, text="Network History"
        )
        right_frame = tk.LabelFrame(
            middle_frame,
            bg=BACKGROUND,
            fg=FOREGROUND,
            text="Info",
            padx=10,
            pady=10,
        )
        bottom_frame = tk.Frame(main_frame, bg=BACKGROUND)

        join_button = self.formatted_buttons(
            bottom_frame,
            text="Join",
            command=lambda: join_network(network_entry_value.get()),
        )
        delete_history_entry_button = self.formatted_buttons(
            bottom_frame,
            text="Delete history entry",
            command=delete_history_entry,
        )

        join_title = tk.Label(
            main_frame, text="Join Network", font="Monospace"
        )
        network_history_list = TreeView(left_frame, "Network")
        network_history_scrollbar = tk.Scrollbar(
            left_frame, bd=2, bg=BACKGROUND
        )
        network_history_list.config(
            yscrollcommand=network_history_scrollbar.set
        )
        network_history_scrollbar.config(command=network_history_list.yview)

        network_history_list.style.configure(
            "NoBackground.Treeview", background=BACKGROUND
        )
        network_history_list.configure(
            show="tree", height=20, style="NoBackground.Treeview"
        )
        network_history_list.column("Network", width=300)
        network_history_list.bind("<<TreeviewSelect>>", on_network_selected)
        network_history_list.bind(
            "<Double-Button-1>", lambda _a: join_button.invoke()
        )

        join_label = tk.Label(
            bottom_frame, text="Network ID:", bg=BACKGROUND, fg=FOREGROUND
        )
        join_entry = tk.Entry(
            bottom_frame,
            width=20,
            font="Monospace",
            textvariable=network_entry_value,
        )

        network_id_label = tk.Label(
            right_frame, font=("Monospace", 11), width=45, anchor="w"
        )
        network_name_label = tk.Label(
            right_frame, font=("Monospace", 11), width=45, anchor="w"
        )
        last_joined_label = tk.Label(
            right_frame,
            font=("Monospace", 11),
            width=45,
            anchor="w",
        )
        currently_joined_label = tk.Label(
            right_frame,
            font=("Monospace", 11),
            width=45,
            anchor="w",
        )

        close_button = self.formatted_buttons(
            bottom_frame,
            text="Close",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=lambda: join_window.destroy(),
        )

        populate_network_list()
        populate_info_sidebar()

        join_title.pack(side="top")
        network_history_list.pack(side="left", padx=10, pady=10)
        network_history_scrollbar.pack(side="right", fill="y")

        network_id_label.pack(side="top", anchor="w")
        network_name_label.pack(side="top", anchor="w")
        last_joined_label.pack(side="top", anchor="w")
        currently_joined_label.pack(side="top", anchor="w")

        join_label.pack(side="left", anchor="w", pady=10)
        join_entry.pack(side="left", anchor="w", pady=10)
        join_button.pack(side="left", pady=10)
        delete_history_entry_button.pack(side="left", pady=10)
        close_button.pack(side="right", pady=10)

        left_frame.pack(side="left", fill="y", pady=10, padx=5)
        right_frame.pack(side="right", fill="y", pady=10, padx=5)
        middle_frame.pack(side="top", fill="both")
        bottom_frame.pack(side="top", fill="both")
        main_frame.pack(side="top", fill="x")

    def leave_network(self):
        # get selected network
        try:
            selectionId = int(self.networkList.focus())
            selectionInfo = self.networkList.item(selectionId)
        except TypeError:
            messagebox.showinfo(
                icon="info", title="Error", message="No network selected"
            )
            return
        network = selectionInfo["values"][0]
        networkName = selectionInfo["values"][1]
        answer = messagebox.askyesno(
            title="Leave Network",
            message=f"Are you sure you want to "
            f'leave "{networkName}" (ID: {network})?',
        )
        if answer:
            try:
                run_zerotier_cli("leave", network)
                leaveResult = "Successfully left network"
            except CalledProcessError:
                leaveResult = "Error"
        else:
            return
        messagebox.showinfo(icon="info", message=leaveResult)
        self.refresh_networks()

    def get_status(self):
        status = run_zerotier_cli("status")
        status = status.split()
        return status

    def about_window(self):
        statusWindow = self.launch_sub_window("About")
        status = self.get_status()

        # frames
        topFrame = tk.Frame(statusWindow, padx=20, pady=30, bg=BACKGROUND)
        middleFrame = tk.Frame(statusWindow, padx=20, pady=10, bg=BACKGROUND)
        bottomTopFrame = tk.Frame(
            statusWindow, padx=20, pady=10, bg=BACKGROUND
        )
        bottomFrame = tk.Frame(statusWindow, padx=20, pady=10, bg=BACKGROUND)

        # widgets
        titleLabel = tk.Label(
            topFrame,
            text="ZeroTier GUI",
            font=70,
            bg=BACKGROUND,
            fg=FOREGROUND,
        )

        ztAddrLabel = self.selectable_text(
            middleFrame,
            font="Monospace",
            text="{:40s}{}".format("My ZeroTier Address:", status[2]),
        )
        versionLabel = tk.Label(
            middleFrame,
            font="Monospace",
            text="{:40s}{}".format("ZeroTier Version:", status[3]),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        ztGuiVersionLabel = tk.Label(
            middleFrame,
            font="Monospace",
            text="{:40s}{}".format("ZeroTier GUI (Upgraded) Version:", "2.7.1"),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        statusLabel = tk.Label(
            middleFrame,
            font="Monospace",
            text="{:40s}{}".format("Status:", status[4]),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )

        closeButton = self.formatted_buttons(
            bottomTopFrame,
            text="Close",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=lambda: statusWindow.destroy(),
        )

        # credits
        creditsLabel1 = tk.Label(
            bottomFrame,
            text="GUI originally created by Tomás Ralph",
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        creditsLabel2 = self.selectable_text(
            bottomFrame,
            text="github.com/tralph3/zerotier-gui",
            justify="center",
        )
        creditsLabel3 = tk.Label(
            bottomFrame,
            text="GUI upgraded and packaged by Aaron Collins",
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        creditsLabel4 = self.selectable_text(
            bottomFrame,
            text="github.com/aaron777collins/ZeroTier-GUI-Arch",
            justify="center",
        )

        # pack widgets
        titleLabel.pack(side="top", anchor="n")

        ztAddrLabel.pack(side="top", anchor="w")
        versionLabel.pack(side="top", anchor="w")
        ztGuiVersionLabel.pack(side="top", anchor="w")
        statusLabel.pack(side="top", anchor="w")

        closeButton.pack(side="top")

        creditsLabel1.pack(side="top", fill="x")
        creditsLabel2.pack(side="top")
        creditsLabel3.pack(side="top", fill="x")
        creditsLabel4.pack(side="top")

        topFrame.pack(side="top", fill="both")
        middleFrame.pack(side="top", fill="both")
        bottomTopFrame.pack(side="top", fill="both")
        bottomFrame.pack(side="top", fill="both")

        statusWindow.mainloop()

    def get_interface_state(self, interface):
        res = run_command(["ip", "--json", "address"])
        # print(res)
        sres = res.strip()
        # print(sres)
        jres = json.loads(sres)
        # print(jres)
        interfaceInfo = jres
        for info in interfaceInfo:
            if info["ifname"] == interface:
                state = info["operstate"]
                break
            state = "UNKNOWN"

        return state

    def toggle_interface_connection(self):
        try:
            idInList = int(self.networkList.focus())
        except TypeError:
            messagebox.showinfo(
                icon="info", title="Error", message="No network selected"
            )
            return

        # id in list will always be the same as id in json
        # because the list is generated in the same order
        currentNetworkInfo = self.get_networks_info()[idInList]
        currentNetworkInterface = currentNetworkInfo["portDeviceName"]

        state = self.get_interface_state(currentNetworkInterface)

        if state.lower() == "down":
            run_command(["pkexec", "ip", "link", "set", currentNetworkInterface, "up"])
        else:
            run_command(
                    ["pkexec",
                    "ip",
                    "link",
                    "set",
                    currentNetworkInterface,
                    "down"]
            )

        self.refresh_networks()

    def see_peer_paths(self, peerList):
        try:
            idInList = int(peerList.focus())
        except TypeError:
            messagebox.showinfo(
                icon="info", title="Error", message="No peer selected"
            )
            return

        info = peerList.item(idInList)
        peerId = info["values"][0]

        pathsWindow = self.launch_sub_window("Peer Path")
        pathsWindow.configure(bg=BACKGROUND)

        # frames
        topFrame = tk.Frame(pathsWindow, padx=20, bg=BACKGROUND)
        middleFrame = tk.Frame(pathsWindow, padx=20, bg=BACKGROUND)
        bottomFrame = tk.Frame(pathsWindow, padx=20, pady=10, bg=BACKGROUND)

        # widgets
        peerIdLabel = tk.Label(
            topFrame,
            font=40,
            bg=BACKGROUND,
            fg=FOREGROUND,
            text=f'Seeing paths for peer with ID "{str(peerId)}"',
        )
        pathsListScrollbar = tk.Scrollbar(middleFrame, bd=2, bg=BACKGROUND)
        pathsList = TreeView(
            middleFrame,
            "Active",
            "Address",
            "Expired",
            "Last Receive",
            "Last Send",
            "Preferred",
            "Trusted Path ID",
        )

        closeButton = self.formatted_buttons(
            bottomFrame,
            text="Close",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=lambda: pathsWindow.destroy(),
        )
        refreshButton = self.formatted_buttons(
            bottomFrame,
            text="Refresh Paths",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=lambda: self.refresh_paths(pathsList, idInList),
        )

        # pack widgets
        peerIdLabel.pack(side="left", fill="both")
        pathsListScrollbar.pack(side="right", fill="both")
        pathsList.pack(side="bottom", fill="x")

        closeButton.pack(side="left", fill="x")
        refreshButton.pack(side="right", fill="x")

        topFrame.pack(side="top", fill="x", pady=(30, 0))
        middleFrame.pack(side="top", fill="x")
        bottomFrame.pack(side="top", fill="x")

        self.refresh_paths(pathsList, idInList)
        pathsList.config(yscrollcommand=pathsListScrollbar.set)
        pathsListScrollbar.config(command=pathsList.yview)

        pathsWindow.mainloop()

    def see_peers(self):
        def call_see_peer_paths(_event):
            self.see_peer_paths(peersList)

        peersWindow = self.launch_sub_window("Peers")
        peersWindow.configure(bg=BACKGROUND)

        # frames
        topFrame = tk.Frame(peersWindow, padx=20, bg=BACKGROUND)
        middleFrame = tk.Frame(peersWindow, padx=20, bg=BACKGROUND)
        bottomFrame = tk.Frame(peersWindow, padx=20, pady=10, bg=BACKGROUND)

        # widgets
        peersListScrollbar = tk.Scrollbar(middleFrame, bd=2, bg=BACKGROUND)
        peersList = TreeView(
            middleFrame, "ZT Address", "Version", "Role", "Latency"
        )
        peersList.bind("<Double-Button-1>", call_see_peer_paths)

        closeButton = self.formatted_buttons(
            bottomFrame,
            text="Close",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=lambda: peersWindow.destroy(),
        )
        refreshButton = self.formatted_buttons(
            bottomFrame,
            text="Refresh Peers",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=lambda: self.refresh_peers(peersList),
        )
        seePathsButton = self.formatted_buttons(
            bottomFrame,
            text="See Paths",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=lambda: self.see_peer_paths(peersList),
        )

        # pack widgets
        peersListScrollbar.pack(side="right", fill="both")
        peersList.pack(side="bottom", fill="x")

        closeButton.pack(side="left", fill="x")
        refreshButton.pack(side="right", fill="x")
        seePathsButton.pack(side="right", fill="x")

        topFrame.pack(side="top", fill="x", pady=(30, 0))
        middleFrame.pack(side="top", fill="x")
        bottomFrame.pack(side="top", fill="x")
        self.refresh_peers(peersList)

        peersList.config(yscrollcommand=peersListScrollbar.set)
        peersListScrollbar.config(command=peersList.yview)

        peersWindow.mainloop()

    def see_network_info(self):
        try:
            idInList = int(self.networkList.focus())
        except TypeError:
            messagebox.showinfo(
                icon="info", title="Error", message="No network selected"
            )
            return
        infoWindow = self.launch_sub_window("Network Info")

        # id in list will always be the same as id in json
        # because the list is generated in the same order
        currentNetworkInfo = self.get_networks_info()[idInList]

        # frames
        topFrame = tk.Frame(infoWindow, pady=30, bg=BACKGROUND)
        middleFrame = tk.Frame(infoWindow, padx=20, bg=BACKGROUND)

        allowDefaultFrame = tk.Frame(infoWindow, padx=20, bg=BACKGROUND)
        allowGlobalFrame = tk.Frame(infoWindow, padx=20, bg=BACKGROUND)
        allowManagedFrame = tk.Frame(infoWindow, padx=20, bg=BACKGROUND)
        allowDNSFrame = tk.Frame(infoWindow, padx=20, bg=BACKGROUND)

        bottomFrame = tk.Frame(infoWindow, pady=10, bg=BACKGROUND)

        # check variables
        allowDefault = tk.BooleanVar()
        allowGlobal = tk.BooleanVar()
        allowManaged = tk.BooleanVar()
        allowDNS = tk.BooleanVar()

        allowDefault.set(currentNetworkInfo["allowDefault"])
        allowGlobal.set(currentNetworkInfo["allowGlobal"])
        allowManaged.set(currentNetworkInfo["allowManaged"])
        allowDNS.set(currentNetworkInfo["allowDNS"])

        # assigned addresses widget generation
        try:
            assignedAddressesWidgets = []

            # first widget
            assignedAddressesWidgets.append(
                self.selectable_text(
                    middleFrame,
                    "{:25s}{}".format(
                        "Assigned Addresses:",
                        currentNetworkInfo["assignedAddresses"][0],
                    ),
                    font="Monospace",
                )
            )

            # subsequent widgets
            for address in currentNetworkInfo["assignedAddresses"][1:]:
                assignedAddressesWidgets.append(
                    self.selectable_text(
                        middleFrame,
                        "{:>42s}".format(address),
                        font="Monospace",
                    )
                )
        except IndexError:
            assignedAddressesWidgets.append(
                self.selectable_text(
                    middleFrame,
                    "{:25s}{}".format("Assigned Addresses:", "-"),
                    font="Monospace",
                )
            )

        # widgets
        titleLabel = tk.Label(
            topFrame,
            text="Network Info",
            font=70,
            bg=BACKGROUND,
            fg=FOREGROUND,
        )

        nameLabel = self.selectable_text(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format("Name:", currentNetworkInfo["name"]),
        )
        idLabel = self.selectable_text(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format("Network ID:", currentNetworkInfo["id"]),
        )
        statusLabel = tk.Label(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format("Status:", currentNetworkInfo["status"]),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        stateLabel = tk.Label(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format(
                "State:",
                self.get_interface_state(currentNetworkInfo["portDeviceName"]),
            ),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        typeLabel = tk.Label(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format("Type:", currentNetworkInfo["type"]),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        deviceLabel = self.selectable_text(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format(
                "Device:", currentNetworkInfo["portDeviceName"]
            ),
        )
        bridgeLabel = tk.Label(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format("Bridge:", currentNetworkInfo["bridge"]),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        macLabel = self.selectable_text(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format("MAC Address:", currentNetworkInfo["mac"]),
        )
        mtuLabel = self.selectable_text(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format("MTU:", currentNetworkInfo["mtu"]),
        )
        dhcpLabel = tk.Label(
            middleFrame,
            font="Monospace",
            text="{:25s}{}".format("DHCP:", currentNetworkInfo["dhcp"]),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )

        allowDefaultLabel = tk.Label(
            allowDefaultFrame,
            font="Monospace",
            text="{:24s}".format("Allow Default Route"),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        allowDefaultCheck = tk.Checkbutton(
            allowDefaultFrame,
            variable=allowDefault,
            command=lambda: change_config("allowDefault", allowDefault.get()),
            bg=BACKGROUND,
            fg=FOREGROUND,
            highlightthickness=0,
        )

        allowGlobalLabel = tk.Label(
            allowGlobalFrame,
            font="Monospace",
            text="{:24s}".format("Allow Global IP"),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        allowGlobalCheck = tk.Checkbutton(
            allowGlobalFrame,
            variable=allowGlobal,
            command=lambda: change_config("allowGlobal", allowGlobal.get()),
            bg=BACKGROUND,
            fg=FOREGROUND,
            highlightthickness=0,
        )

        allowManagedLabel = tk.Label(
            allowManagedFrame,
            font="Monospace",
            text="{:24s}".format("Allow Managed IP"),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        allowManagedCheck = tk.Checkbutton(
            allowManagedFrame,
            variable=allowManaged,
            command=lambda: change_config("allowManaged", allowManaged.get()),
            bg=BACKGROUND,
            fg=FOREGROUND,
            highlightthickness=0,
        )

        allowDNSLabel = tk.Label(
            allowDNSFrame,
            font="Monospace",
            text="{:24s}".format("Allow DNS Configuration"),
            bg=BACKGROUND,
            fg=FOREGROUND,
        )
        allowDNSCheck = tk.Checkbutton(
            allowDNSFrame,
            variable=allowDNS,
            command=lambda: change_config("allowDNS", allowDNS.get()),
            bg=BACKGROUND,
            fg=FOREGROUND,
            highlightthickness=0,
        )

        closeButton = self.formatted_buttons(
            bottomFrame,
            text="Close",
            bg=BUTTON_BACKGROUND,
            activebackground=BUTTON_ACTIVE_BACKGROUND,
            command=lambda: infoWindow.destroy(),
        )

        # pack widgets
        titleLabel.pack(side="top", anchor="n")

        nameLabel.pack(side="top", anchor="w")
        idLabel.pack(side="top", anchor="w")

        # assigned addresses
        for widget in assignedAddressesWidgets:
            widget.pack(side="top", anchor="w")

        statusLabel.pack(side="top", anchor="w")
        stateLabel.pack(side="top", anchor="w")
        typeLabel.pack(side="top", anchor="w")
        deviceLabel.pack(side="top", anchor="w")
        bridgeLabel.pack(side="top", anchor="w")
        macLabel.pack(side="top", anchor="w")
        mtuLabel.pack(side="top", anchor="w")
        dhcpLabel.pack(side="top", anchor="w")

        allowDefaultLabel.pack(side="left", anchor="w")
        allowDefaultCheck.pack(side="left", anchor="w")

        allowGlobalLabel.pack(side="left", anchor="w")
        allowGlobalCheck.pack(side="left", anchor="w")

        allowManagedLabel.pack(side="left", anchor="w")
        allowManagedCheck.pack(side="left", anchor="w")

        allowDNSLabel.pack(side="left", anchor="w")
        allowDNSCheck.pack(side="left", anchor="w")

        closeButton.pack(side="top")

        topFrame.pack(side="top", fill="both")
        middleFrame.pack(side="top", fill="both")

        allowDefaultFrame.pack(side="top", fill="both")
        allowGlobalFrame.pack(side="top", fill="both")
        allowManagedFrame.pack(side="top", fill="both")
        allowDNSFrame.pack(side="top", fill="both")

        bottomFrame.pack(side="top", fill="both")

        # checkbutton functions
        def change_config(config, value):
            # zerotier-cli only accepts int values
            value = int(value)
            try:
                run_zerotier_cli(
                        "set",
                        currentNetworkInfo["id"],
                        f"{config}={value}",
                    stderr_to_stdout=True,
                )
            except CalledProcessError as error:
                error = error.output.strip()
                messagebox.showinfo(
                    title="Error", message=f'Error: "{error}"', icon="error"
                )

        # needed to stop local variables from being destroyed before the window
        infoWindow.mainloop()

    def on_exit(self):
        self.save_network_history()
        self.window.destroy()


class TreeView(ttk.Treeview):
    def __init__(self, root, *columns):
        super().__init__(root)

        self["columns"] = tuple(columns)
        for label in columns:
            self.heading(label, text=label)
        self.configure_style()

    def configure_style(self):
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("Monospace", 11))
        self.style.configure("Treeview", font=("Monospace", 11))
        self.style.layout(
            "Treeview", [("Treeview.treearea", {"sticky": "nswe"})]
        )
        self.tag_configure("odd", background="#fcfcfc")
        self.tag_configure("even", background="#eeeeee")
        self.tag_configure("disabled", background="#d14444")

    def insert(self, values, disabled=False, **kwargs):
        item_count = len(self.get_children())
        tag = "even" if item_count % 2 == 0 else "odd"
        if disabled:
            tag = "disabled"
        super().insert(
            "", tk.END, iid=item_count, values=values, tags=tag, **kwargs
        )


def manage_service(action, cdw=None):

    user = get_user().strip()
    cdwPath = f"/home/{user}" if cdw is None else cdw

    # try as user
    try:
        return run_command(["systemctl", "--user", action, "zerotier-one"], use_sudo=False, cdw=cdwPath)
    except CalledProcessError:
        # try as system
        try:
            return run_command(["systemctl", action, "zerotier-one"], cdw=cdwPath)
        except CalledProcessError as error:
            error = error.output.decode().strip()
            messagebox.showinfo(
                title="Error", message=f'Error: "{error}"', icon="error"
            )

def reinstall_backend():

    user = get_user().strip()
    cdwPath = f"/home/{user}"

    # stop service
    try:
        manage_service("stop")
        manage_service("disable")
    except CalledProcessError as error:
        # Check if error code is 5
        if error.returncode == 5:
            # The service could not be loaded
            print(f"Service could not be loaded: {error}, error.returncode: {error.returncode}")
        else:
            print("An unknown error occurred while trying to stop and disable the ZeroTier service. Skipping the stop/disable step and proceeding with the re-installation of the backend service anyways.")

    # Run download_and_reinstall_backend.sh as regular user using bash
    try:
        # sh -c 'curl -s https://raw.githubusercontent.com/aaron777collins/ZeroTier-GUI-Arch/master/download_and_reinstall_backend.sh | bash
        run_command(
            ["sh", "-c", "curl -s https://raw.githubusercontent.com/aaron777collins/ZeroTier-GUI-Arch/master/download_and_reinstall_backend.sh | bash"],
            use_sudo=False,
            cdw=cdwPath,
        )

        # Tell the user we succeeded in re-installing the backend
        messagebox.showinfo(
            title="Success",
            message="Successfully re-installed the ZeroTier backend.",
            icon="info",
        )

    except CalledProcessError as error:
        error = error.output.decode().strip()
        messagebox.showinfo(
            title="Error", message=f'Error: "{error}"', icon="error"
        )

        # Tell user that we failed to re-install the backend and that they should delete the ~/.zerotier-one folder and re-run the installer script (possibly a few times) in a messagebox
        messagebox.showinfo(
            title="Error",
            message="Failed to re-install the ZeroTier backend.\n\n"
            "Please delete the ~/.zerotier-one folder and re-run the installer script.",
            icon="error",
        )

        exit(1)

    # start service
    manage_service("enable")
    manage_service("start")





def get_user():
    return pwd.getpwuid(os.getuid())[0]

def run_command(command, use_sudo=True, cdw=None):
    user = get_user().strip()

    cdwPath = f"/home/{user}/.zerotier-one" if cdw is None else cdw

    print(f"Original command: {command}, cdwPath: {cdwPath}, use_sudo: {use_sudo}")

    # Check if /home/<user>/.zerotier-one exists
    if not os.path.exists(cdwPath):
        raise FileNotFoundError(f"Path {cdwPath} does not exist")

    # Add prefixes

    if use_sudo:
        command = ['sudo', '-S'] + command

    if not DEBUG_MODE:
        command = ['flatpak-spawn', '--host'] + command

    print(f"Running command: {command}")
    process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cdwPath)

    if use_sudo:
        # get user
        stdout, stderr = process.communicate(input=(SUDO_PASSWORD + '\n').encode())
    else:
        stdout, stderr = process.communicate()

    try:
        # If none, print None otherwise decode
        stdoutStr = stdout.decode().replace(f"[sudo] password for {get_user()}: ", "") if stdout is not None else None
        stderrStr = stderr.decode() if stderr is not None else None
        print(f'stdout: {stdoutStr}, stderr: {stderrStr}, process.returncode: {process.returncode}')
    except Exception as e:
        print("An error occurred while trying to print the stdout, stderr, and process.returncode. Printing in raw format instead.")
        print(f"stdout: {stdout}, stderr: {stderr}, process.returncode: {process.returncode}")

    if process.returncode != 0:
        raise CalledProcessError(process.returncode, command, output=stdout)

    # Strip [sudo] password for <user>: from stdout
    return stdout.decode().replace(f"[sudo] password for {get_user()}: ", "")

def disable_duplicate_zerotier():
    # Detect if there's a duplicate zerotier service that is running. If so, ask the user permission to disable it and mention that not disabling it could lead to issues running our ZeroTier service.
    # If the user agrees, disable the duplicate service and tell the user that it has been disabled.

    # Check if the service is running
    try:
        res = run_command(["systemctl", "is-active", "zerotier-one"])

        if "active" in res:
            print("Duplicate ZeroTier service detected. Asking user for permission to disable it.")
            # Ask the user if they'd like to disable the duplicate ZeroTier service
            disableResponse = messagebox.askyesno(
                title="Duplicate ZeroTier Service Detected",
                message="A duplicate ZeroTier service has been detected. This could cause issues with the ZeroTier service. Would you like to disable the duplicate ZeroTier service?",
                icon="warning",
            )

            if disableResponse:
                # Disable the duplicate ZeroTier service
                print("Disabling the duplicate ZeroTier service.")
                run_command(["systemctl", "disable", "zerotier-one"])
                run_command(["systemctl", "stop", "zerotier-one"])
                print("Disabled the duplicate ZeroTier service.")
                # Tell the user that the duplicate ZeroTier service has been disabled
                messagebox.showinfo(
                    title="Duplicate ZeroTier Service Disabled",
                    message="The duplicate ZeroTier service has been disabled.",
                    icon="info",
                )
    except Exception as e:
        print(f"An unknown error occurred while trying to check if the ZeroTier service is running. Error: {e}")
        return


def run_zerotier_cli(*args, stderr_to_stdout=False):
    user = get_user().strip()
    command = ['sudo', '-S', './zerotier-cli', f"-D/home/{user}/.zerotier-one"] + list(args)
    if not DEBUG_MODE:
        command = ['flatpak-spawn', '--host'] + command
    stderr = STDOUT if stderr_to_stdout else PIPE
    process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=stderr, cwd=f"/home/{user}/.zerotier-one")
    stdout, stderr = process.communicate(input=(SUDO_PASSWORD + '\n').encode())
    if process.returncode != 0:
        raise CalledProcessError(process.returncode, command, output=stdout)
    return stdout.decode()

def ask_sudo_password():
    def save_password(event=None):
        nonlocal password
        password = passwordEntry.get()
        passwordWindow.destroy()

    password = None

    # Create a new Toplevel window instead of Tk
    passwordWindow = tk.Toplevel()
    passwordWindow.title("Enter Sudo Password")

    # frames
    topFrame = tk.Frame(passwordWindow, padx=20, pady=20, bg='white')
    bottomFrame = tk.Frame(passwordWindow, padx=20, pady=10, bg='white')

    # widgets
    promptLabel = tk.Label(
        topFrame,
        text="Please enter your sudo password:",
        font=("Helvetica", 14),
        bg='white',
        fg='black',
    )

    passwordEntry = tk.Entry(
        topFrame,
        show='*',
        font=("Monospace", 12),
        bg='white',
        fg='black',
    )

    saveButton = tk.Button(
        bottomFrame,
        text="Submit",
        bg='DarkOrange1',
        activebackground='DarkOrange2',
        command=save_password,
    )

    # Bind the Enter key to the save_password function
    passwordEntry.bind('<Return>', save_password)

    # pack widgets
    promptLabel.pack(side="top", anchor="n")
    passwordEntry.pack(side="top", anchor="n", pady=10)
    saveButton.pack(side="top", pady=10)

    topFrame.pack(side="top", fill="both")
    bottomFrame.pack(side="top", fill="both")

    # Focus on the password entry box
    passwordEntry.focus_set()

    # Wait for the window to close
    passwordWindow.grab_set()
    passwordWindow.wait_window()

    return password


if __name__ == "__main__":
    os.environ["FLATPAK_ID"] = "io.github.aaron777collins.zerotier-gui"
    # temporary window for popups
    tmp = tk.Tk()
    tmp.withdraw()

    SUDO_PASSWORD = ask_sudo_password()
    print(f"Entered password: {SUDO_PASSWORD}")

    # while loop, forcing the user to give a proper sudo password

    while True:
        try:
            run_command(["true"])
            break
        except CalledProcessError:
            SUDO_PASSWORD = ask_sudo_password()
            print(f"Entered password: {SUDO_PASSWORD}")
        except FileNotFoundError:
            messagebox.showinfo(
                    title="Error",
                    message="ZeroTier isn't installed! Re-installing the backend...",
                    icon="error",
                )
            reinstall_backend()
            continue
        except Exception as e:
            # Tell the user the error like "message=f"An error while trying to run any basic commands. Please report the following error: {e} on Github. You can also try re-installing the backend to see if that fixes it.
            # Ask them if they'd like to try it (yes/no)
            # If they say yes, reinstall the backend
            # If they say no, tell them to report the error on Github
            fixResponse = messagebox.askyesno(
                title="Error",
                message=f"An error occurred while trying to run basic commands. Please report the following error: {e} on the ZeroTier-Arch Github.\n\nOptionally: you can try self diagnosis:\nWould you like to try re-installing the backend?",
                icon="error",
            )
            if fixResponse:
                reinstall_backend()
                continue
            else:
                messagebox.showinfo(
                    title="Error",
                    message=f"Please report the error on the ZeroTier-Arch Github: {e}\n\nLink: https://github.com/aaron777collins/ZeroTier-GUI-Arch/issues/new",
                    icon="error",
                )
                exit(1)
            continue

    # Check for Root level ZeroTier installation (from other installations, etc.) and disable it
    disable_duplicate_zerotier()

    # simple check for zerotier
    while True:
        try:
            run_zerotier_cli("listnetworks")
        # in case the command throws an error
        except CalledProcessError as error:
            # no zerotier authtoken
            if error.returncode == 2:
                messagebox.showinfo(
                    title="Error",
                    icon="error",
                    message="This user doesn't have access to ZeroTier! Re-installing the backend...",
                )
                reinstall_backend()
                continue
            # service not running
            if error.returncode == 1:
                messagebox.showinfo(
                    title="Error",
                    icon="error",
                    message="The zerotier service isn't running! Starting the backend...",
                )

                # start the service
                manage_service("start")

                # check if the service is running (run_command(["systemctl", "--user", "is-active", "zerotier-one"])) and check if the response contains active or inactive
                user = get_user().strip()
                running = run_command(["systemctl", "--user", "is-active", "zerotier-one"], use_sudo=False, cdw=f"/home/{user}")
                if "inactive" in running or "failed" in running:
                    messagebox.showinfo(
                        title="Error",
                        icon="error",
                        message="Failed to start the ZeroTier backend. Re-installing the backend...",
                    )
                    reinstall_backend()
                    continue
                else:
                    messagebox.showinfo(
                        title="Success",
                        icon="info",
                        message="Successfully started the ZeroTier backend.",
                    )
                    continue

            # in case there's no command
            if error.returncode == 127:
                messagebox.showinfo(
                    title="Error",
                    message="ZeroTier isn't installed! Re-installing the backend...",
                    icon="error",
                )
                reinstall_backend()
                continue
            break
        except FileNotFoundError:
            messagebox.showinfo(
                    title="Error",
                    message="ZeroTier isn't installed! Re-installing the backend...",
                    icon="error",
                )
            reinstall_backend()
            continue
        break
    # destroy temporary window
    tmp.destroy()
    # create mainwindow class and execute the mainloop
    mainWindow = MainWindow()
    mainWindow.window.protocol("WM_DELETE_WINDOW", mainWindow.on_exit)
    mainWindow.window.mainloop()
