#!/bin/bash

x11_pkgs=(
	xclip
	xorg
	xorg-xinit
	libx11
	xdotool
	xrectsel
)

paru --sudo=doas -S --needed "${x11_pkgs[@]}"
cp -rf ./etc/X11/xorg.conf.d /etc/X11 || exit 1
