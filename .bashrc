source "$HOME/.config/shell/aliases.sh"
source "$HOME/.config/shell/utils.sh"
source "$HOME/.config/shell/setup.sh"

PS1='[\u@\h \W]\$ '

# If not running interactively, don't do anything
[[ $- != *i* ]] && return


#ignore upper and lowercase when TAB completion
bind "set completion-ignore-case on"

#shopt
shopt -s autocd # change to named directory
shopt -s cdspell # autocorrects cd misspellings
shopt -s cmdhist # save multi-line commands in history as single line
shopt -s dotglob
shopt -s histappend # do not overwrite history
shopt -s expand_aliases # expand aliases

# History in cache directory:
HISTSIZE=1000000000
SAVEHIST=1000000000
HISTFILE=~/.shell_history

