alias lsc='/usr/bin/ls --color=auto' # Default ls with colors
# alias ls='logo-ls -Dh' # Modern ls https://github.com/Yash-Handa/logo-ls
alias jls='jls -lh'
alias ls='eza --icons'
alias l='ls -lh'

# navigation
alias ~='cd ~'
alias .-='cd -'
alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../..'
alias .3='cd ../../..'
alias .4='cd ../../../..'
alias .5='cd ../../../../..'

# Show the current path with (jpwd)
alias .='pwd'

# Edit something
alias e="$EDITOR"

# Read file
alias r='bat'

# General
alias c='cargo'
alias ct='cargo test'
alias m='make'
alias o='xdg-open'
alias vimdiff='nvim -d'
alias clip='xclip -selection clipboard'
alias bash='SHELL=bash bash'
alias zsh='SHELL=zsh zsh'
alias fish='SHELL=fish fish'

# Keybase
alias ks='keybase chat send'
alias ksr='keybase chat read'
alias kl='keybase chat list'


# Git
alias g='git'
alias gc='git checkout'
alias push='git push'
alias pusht='push --tags'
alias pushf='push --force'
alias commit='git commit -S'
alias clone='git clone'
alias add='git add'
alias status='git status'
alias pull='git pull'
alias fetch='git fetch'
alias rebase='git rebase'
alias tag='git tag'
alias ctag='tag --sign'
alias switch='git switch'
alias gah='git stash && git pull --rebase && git stash pop'
alias pr='gh pr create -t $(git show -s --format=%s HEAD) -b $(git show -s --format=%B HEAD | tail -n+3)'

# Colorize grep output (good for log files)
alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'

# confirm before overwriting something
alias cp="cp -i"
alias mv='mv -i'
# alias rm='rm -i'

#youtube download
alias yta-aac="yt-dlp --extract-audio --audio-format aac "
alias yta-best="yt-dlp --extract-audio --audio-format best "
alias yta-flac="yt-dlp --extract-audio --audio-format flac "
alias yta-mp3="yt-dlp --extract-audio --audio-format mp3 "
alias ytv-best="yt-dlp -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio' --merge-output-format mp4 "

# Arch
alias paru="paru --sudo $SUDO"
install() {
    $SUDO pacman -S $@ || $AURHELPER -S $@
}
search() {
    pacman -Ss $@ || $AURHELPER -Ss $@
}
update() {
    $SUDO pacman -Su || $AURHELPER -Su
}
remove() {
    $SUDO pacman -Rns $@
}
alias i='install'
alias s='search'
alias u='update'
alias un='remove'
alias fuck-my-lap='sudo pacman -Syyu'


