#!/bin/bash


printf "Installing the AUR helper (paru)"
current_path="$(pwd)"
cd /tmp || exit 1
git clone --depth=1 https://aur.archlinux.org/paru.git
cd paru || exit 1
makepkg -si
cd "$current_path" || exit 1
