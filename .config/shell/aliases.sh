alias lsc='/usr/bin/ls --color=auto' # Default ls with colors
# alias ls='logo-ls -Dh' # Modern ls https://github.com/Yash-Handa/logo-ls
alias jls='jls -lh'
alias ls='jls'
alias neofetch='neofetch --kitty /mnt/Data/Personalize/Wallpapers --crop_mode fill --crop_offset center --xoffset 1 --yoffset 1'
alias nfe='neofetch'

# navigation
alias ~='cd ~'
alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../..'
alias .3='cd ../../..'
alias .4='cd ../../../..'
alias .5='cd ../../../../..'

# Show the current path with (jpwd)
alias .='jpwd'

# Edit something
alias e="$EDITOR"

# Read the file
alias r='bat'

# Git
alias gp='git push'
alias commit='git commit -S'
alias clone='git clone'

# Colorize grep output (good for log files)
alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'


# confirm before overwriting something
alias cp="cp -i"
alias mv='mv -i'
# alias rm='rm -i'

# Update
alias fuck-my-lap='sudo pacman -Syyu'

