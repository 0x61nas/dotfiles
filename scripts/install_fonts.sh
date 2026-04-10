#!/bin/bash

set -e
if [[ $(id -u) -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi

fonts_pkgs=(
	ttf-jetbrains-mono-nerd
	ttf-roboto
	ttf-hack
	ttf-hack-nerd
	gnu-free-fonts
	ttf-sazanami
	ttf-fira-code
	noto-fonts-emoji
	noto-fonts-extra
	noto-fonts
	adobe-source-code-pro-fonts
	ttf-roboto-mono
	ttf-nerd-fonts-symbols-mono
	adobe-source-han-sans-jp-fonts
	adobe-source-sans-fonts
	adobe-source-serif-fonts
)

printf "Installing fonts...\n"
pacman -S --needed "${fonts_pkgs[@]}"

cat << EOF > /etc/fonts/local.conf
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
 <alias>
   <family>sans-serif</family>
   <prefer>
     <family>DejaVu Sans</family>
		 <family>Noto Kufi Arabic</family>
     <family>Noto Sans</family>
     <family>Noto Color Emoji</family>
     <family>Noto Emoji</family>
   </prefer> 
 </alias>

 <alias>
   <family>serif</family>
   <prefer>
     <family>DejaVu Serif</family>
		 <family>Noto Kufi Arabic</family>
     <family>Noto Serif</family>
     <family>Noto Color Emoji</family>
     <family>Noto Emoji</family>
   </prefer>
 </alias>

 <alias>
  <family>monospace</family>
  <prefer>
    <family>DejaVu Sans Mono</family>
		<family>Noto Kufi Arabic</family>
    <family>Noto Mono</family>
    <family>Noto Color Emoji</family>
    <family>Noto Emoji</family>
   </prefer>
 </alias>
</fontconfig>
EOF

fc-cache -v
