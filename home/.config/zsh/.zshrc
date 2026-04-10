source "$HOME/.config/shell/aliases.sh"
source "$HOME/.config/shell/utils.sh"
source "$HOME/.config/shell/setup.sh"
source "$HOME/.config/zsh/functions.zsh"


setopt correct     # Auto corect mistakes
setopt nobeep     # No beep
setopt dvorak    # Use the Dvorak keyboard instead of the standard qwerty keyboard
setopt aliases    # Expand aliases
setopt autocd
setopt cdablevars
setopt multios
# setopt extended_history
setopt inc_append_history_time
setopt autopushd
setopt pushdignoredups
setopt HIST_FCNTL_LOCK
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_EXPIRE_DUPS_FIRST
setopt SHARE_HISTORY
unsetopt EXTENDED_HISTORY

setopt hist_find_no_dups
bindkey '^ ' autosuggest-accept
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

# Enable colors and change prompt:
autoload -U colors && colors
# PS1="%B%{$fg[red]%}[%{$fg[yellow]%}%n%{$fg[green]%}@%{$fg[blue]%}%M %{$fg[magenta]%}%~%{$fg[red]%}]%{$reset_color%}$%b "
source "$HOME/.config/zsh/prompt.zsh"

# PROMPT="%B%{$fg[cyan]%}%(4~|%-1~/.../%2~|%~)%u%b >%{$fg[cyan]%}>%B%(?.% "

DIRSTACKSIZE=25
# History in cache directory:
HISTSIZE=1000000000
SAVEHIST=1000000000
HISTFILE=~/.shell_history

# Basic auto/tab complete:
autoload -U compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "$\{(s.:.)LS_COLORS}"
# zstyle ':completion:*' menu yes
# zstyle ':fzf-tab:complete:cd:*' fzf-preview 'ls --color $realpath'
# zstyle ':fzf-tab:complete:__zoxide_z:*' fzf-preview 'ls --color $realpath'
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path ~/.zsh/cache
zmodload zsh/complist
compinit
_comp_options+=(globdots)		# Include hidden files.

## Plugins section:
# Enable fish style features
ZSH_AUTOSUGGEST_STRATEGY=(history completion)
bindkey '^ ' autosuggest-toggle
source ~/.config/zsh/plugins/zsh-autosuggestions.zsh
# Use syntax highlighting
[[ -e /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]] && 
    source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
# Use history substring search
source ~/.config/zsh/plugins/zsh-history-substring-search.zsh
# source /usr/share/zsh/plugins/fzf-tab-git/fzf-tab.plugin.zsh
source ~/.config/zsh/plugins/nota.zsh
source ~/.config/zsh/plugins/nekojump.plugin.zsh

# Key bindings section
# vi mode
bindkey -v
export KEYTIMEOUT=1

# Use vim keys in tab complete menu:
bindkey -M menuselect 'hyphen' vi-backward-char
bindkey -M menuselect 'k' vi-up-line-or-history
bindkey -M menuselect 'd' vi-forward-char
bindkey -M menuselect 'c' vi-down-line-or-history
bindkey -v '^?' backward-delete-char

# Change cursor shape for different vi modes.
function zle-keymap-select {
  if [[ ${KEYMAP} == vicmd ]] ||
     [[ $1 = 'block' ]]; then
    echo -ne '\e[1 q'
  elif [[ ${KEYMAP} == main ]] ||
       [[ ${KEYMAP} == viins ]] ||
       [[ ${KEYMAP} = '' ]] ||
       [[ $1 = 'beam' ]]; then
    echo -ne '\e[5 q'
  fi
}
zle -N zle-keymap-select
zle-line-init() {
    zle -K viins # initiate `vi insert` as keymap (can be removed if `bindkey -V` has been set elsewhere)
    echo -ne "\e[5 q"
}
zle -N zle-line-init
echo -ne '\e[5 q' # Use beam shape cursor on startup.
preexec() { echo -ne '\e[5 q' ;} # Use beam shape cursor for each new prompt.


# Edit line in vim with ctrl-e:
autoload edit-command-line; zle -N edit-command-line
bindkey '^e' edit-command-line

# bind UP and DOWN arrow keys to history substring search
zmodload zsh/terminfo
bindkey "$terminfo[kcuu1]" history-substring-search-up
bindkey "$terminfo[kcud1]" history-substring-search-down
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

### Functions ###
hst() {
    history 0 | cut -c 8- | uniq | fzf | xclip -selection clipboard
}

ex () {
  if [ -f $1 ] ; then
    case $1 in
      *.tar.bz2)   tar xjf $1   ;;
      *.tar.gz)    tar xzf $1   ;;
      *.bz2)       bunzip2 $1   ;;
      *.rar)       unrar x $1   ;;
      *.gz)        gunzip $1    ;;
      *.tar)       tar xf $1    ;;
      *.tbz2)      tar xjf $1   ;;
      *.tgz)       tar xzf $1   ;;
      *.zip)       unzip $1     ;;
      *.Z)         uncompress $1;;
      *.7z)        7z x $1      ;;
      *.deb)       ar x $1      ;;
      *.tar.xz)    tar xf $1    ;;
      *.tar.zst)   tar xf $1    ;;
      *)           echo "'$1' cannot be extracted via ex()" ;;
    esac
  else
    echo "'$1' is not a valid file"
  fi
}

# Use lf to switch directories and bind it to ctrl-o
lfcd () {
    tmp="$(mktemp)"
    lf -last-dir-path="$tmp" "$@"
    if [ -f "$tmp" ]; then
        dir="$(cat "$tmp")"
        rm -f "$tmp"
        [ -d "$dir" ] && [ "$dir" != "$(pwd)" ] && cd "$dir"
    fi
}
bindkey -s '^o' 'lfcd\n'

checkExtraDev()
{
    [ -z ${extra_dev_shell} ] && return

    addspace=""
    [ ! -z ${extra_packages} ] && addspace=" "
    echo "$extra_dev_shell$addspace"
}


if [[ -n $CUSTOMZSHTOSOURCE ]]; then
  source "$CUSTOMZSHTOSOURCE"
fi

chpwdf() {
    if env | grep -q direnv; then
        extra_dev_shell="direnv"
    else
        if [[ "$extra_dev_shell" = "direnv" ]]; then
            unset extra_dev_shell
        fi
    fi
}

chpwd_functions+=(chpwdf)

GPG_TTY="$(tty)"
export GPG_TTY
gpg-connect-agent updatestartuptty /bye > /dev/null


#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

source /home/anas/.config/broot/launcher/bash/br
