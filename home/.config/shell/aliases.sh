alias lsc='/usr/bin/ls --color=auto' # Default ls with colors
# alias ls='logo-ls -Dh' # Modern ls https://github.com/Yash-Handa/logo-ls
alias jls='jls -lh'
alias ls='eza --icons'
alias l='ls -lh'
alias la='l -a'

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
alias e="\$EDITOR"

# Read file
alias r='bat -p'

# General
alias _="\$SUDO"
alias _!="\$SUDO !!"
alias j="just"
alias cargo='cargo mommy'
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
alias gpush='git push'
alias gpusht='git push --tags'
alias gpushf='git push --force'
alias gcommit='git commit -S'
alias clone='git clone'
alias sclone='git clone --depth=1'
alias gadd='git add'
alias gaddall='git add .'
alias gaddp='git addp'
alias gstat='git status'
alias gpull='git pull -r --autostash'
alias gfetch='git fetch'
alias grebase='git rebase'
alias gtag='git tag'
alias gctag='tag --sign'
alias gswitch='git switch'
alias gah='git stash && git pull --rebase && git stash pop'
alias ghpr='gh pr create -t $(git show -s --format=%s HEAD) -b $(git show -s --format=%B HEAD | tail -n+3)'
alias glog='git log --oneline --graph --all'
alias gcm='git commit -m'
alias gcma='git commit -am'
alias gamend='git commit --amend'
alias gpushu='git push -u origin'
alias gsw='git switch'
alias gswc='git switch -c'
alias gbd='git branch -D'
alias gpullff='git pull --ff-only'
alias gfetchm='git fetch origin main'
alias grho='git reset --hard origin/main'
alias gcof='git checkout -- .'
alias grebo='git rebase origin/main'
alias grebi='git rebase -i'
alias grebo_onto='git rebase --onto'
alias gcp='git cherry-pick'
alias gstash='git stash'
alias gpop='git stash pop'
alias gsl='git stash list'
alias grau='git remote add upstream'
alias gbis='git bisect'
alias grfl='git reflog'
alias gclean=' git clean -fdx'
alias gcleani=' git clean -fdxi'

# Colorize grep output (good for log files)
alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'

# confirm before overwriting something
alias cp="cp -vi"
alias mv='mv -vi'
alias rm='rm -v'

#youtube download
alias yta-aac="yt-dlp --extract-audio --audio-format aac "
alias yta-best="yt-dlp --extract-audio --audio-format best "
alias yta-flac="yt-dlp --extract-audio --audio-format flac "
alias yta-mp3="yt-dlp --extract-audio --audio-format mp3 "
alias ytv-best="yt-dlp -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio' --merge-output-format mp4 "

# Docker
alias d='docker'
alias dps='docker ps'
alias dpa='docker ps -a'
alias dimg='docker images'
alias drm='docker rm'
alias drmi='docker rmi'
alias dexec='docker exec -it'
alias dlogs='docker logs -f'

alias dbuild='docker build --network=host -t'
alias drun='docker run --network=host -it'
alias dstart='docker start -ai'
alias drestart='docker restart'

alias dc='docker compose'
alias dcu='docker compose up -d'
alias dcd='docker compose down'
alias dcl='docker compose logs -f'

alias dprune='docker system prune -af'
alias dcleanc='docker container prune -f'
alias dcleani='docker image prune -f'
alias dcleann='docker network prune -f'

alias dinspect='docker inspect'
alias dnet='docker network ls'
alias dvol='docker volume ls'
alias dstop='docker stop'

alias dreset='docker rm -f $(docker ps -aq) && docker rmi -f $(docker images -q)'

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
