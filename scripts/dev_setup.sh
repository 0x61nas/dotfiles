#!/bin/bash

export dev_pkgs=(
	rustup
	gcc
	python
	ruff
	zig
	zls
	uv
	hexyl
	hex
	hurl
	lua
	lua-language-server
	nil-git
	stylua
	bash-language-server
	# asm-lsp # FIXME: OUTDATED
	cloc
	tokei
	gopls
	codespell
	tree-sitter
	tree-sitter-markdown
	tree-sitter-lua
	ltex-ls
	nodejs
	kotlin-language-server
	# jdt-language-server
	# nasmfmt
	# typos
	prettier
	markdownlint-cli2
	plantuml
	git-delta
	nasm
	ctags
	java-runtime-common
	yaml-language-server
)

paru --sudo=doas -S --needed "${dev_pkgs[@]}"
