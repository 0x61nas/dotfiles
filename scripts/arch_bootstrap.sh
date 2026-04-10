#!/bin/env bash

error_exit() {
	echo "$1" > /dev/stderr
	exit 1
}

HOSTNAME="Mayuri"

core_pkgs=(
		intel-ucode
		# base-devel
    archlinux-keyring
		gcc
		autoconf
    automake
    binutils
    bison
    debugedit
    fakeroot
    file
    findutils
    flex
    grep
    groff
    gzip
    libtool
    m4
    make
    pacman
    patch
    pkgconf
    sed
    texinfo
    which
		# fuck sudo
		doas
		git
		tmux
		zsh
		wget
		zoxide
		fzf
		zip unzip
		ffmpeg
		dunst
		btop
		feh
		nvtop
		just
		bc
		neovim
		tlp
		tlp-rdw
		man-db
		man-pages
		networkmanager
		ripgrep
		util-linux
	)

printf "Installing the core packages...\n"
pacman -Syu --needed "${core_pkgs[@]}" || error_exit "Can't install the core packages"

printf "Configure TLP...\n"
cp -f ./etc/tlp.conf /etc/tlp.conf || error_exit "Can't copy the tlp.conf"
systemctl enable --now tlp


# Set the time zone
printf "Configure the time zone (Cairo)...\n"
ln -sf /usr/share/zoneinfo/Africa/Cairo /etc/localtime

# Set the Hardware Clock from the System Clock, and update the timestamps in /etc/adjtime.
hwclock --systohc

# Uncomment desired locales
nvim /etc/locale.gen
# Generate the locales
locale-gen

printf "Set the hostname to %s\n", $HOSTNAME
echo $HOSTNAME > /etc/hostname

# Set the root password
printf "### Please enter a password for the root ###\n"
passwd || error_exit "You must set a root password, idot"

printf "Create the norrmaal user  (anas)\n"
useradd -m anas -G wheel,networkmanager,libvirt,docker,video,audio

printf "Configure doas...\n"
cp -f ./etc/doas.conf /etc/doas.conf || error_exit "Can't copy doas.conf"

printf "Setup the global environment variables...\n"
cp -f ./etc/environment /etc/environment || error_exit "Can't copy the environment file"

printf "Enable Periodic TRIM timer (povided by util-linux)...\n"
systemctl enable fstrim.timer

printf "Installing gpu drivers...\n"
pacman -S --needed nvidia-open

printf "Installing xorg...\n"
pacman -S xorg
cp -rf ./etc/X11/xorg.conf.d /etc/X11 || exit 1

# Aur


printf "Setup the bootloader (systemd boot)...\n"
bootctl install

cat <<EOF > /boot/loader/loader.conf
default @saved
timeout 5
editor yes
console-mode auto
EOF

root_uuid=$(lsblk -o NAME,UUID | grep nvme0n1p2 | awk '{print $NF}')

cat <<EOF > /boot/entries/arch.conf
title   Arch Linux
linux   /vmlinuz-linux
initrd /intel-ucode.img
initrd  /initramfs-linux.img
options splash root=UUID=$root_uuid rw
EOF

cat <<EOF > /boot/entries/arch.conf
title   Arch Linux
linux   /vmlinuz-linux
initrd /intel-ucode.img
initrd  /initramfs-linux.img
options splash root=UUID=$root_uuid rw
EOF


systemctl enable systemd-boot-update.service

printf "Unmute the audio\n"
amixer sset Master unmute
amixer sset Speaker unmute
amixer sset Headphone unmute





echo "${core_pkgs[@]}"
