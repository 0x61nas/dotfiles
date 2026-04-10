#!/bin/bash

zsh_pkgs=(
	# zsh-you-shoud-use
	zsh-syntax-highlighting
	zsh-autosuggestions
	zsh-completions
	zsh-history-substring-search
)

pacman -S "${zsh_pkgs[@]}"
