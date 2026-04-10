# XDG
export XDG_CACHE_HOME=$HOME/.cache
export XDG_CONFIG_HOME=$HOME/.config
export XDG_DATA_HOME=$HOME/.local/share
export XDG_STATE_HOME=$HOME/.local/state

export QT_QPA_PLATFORMTHEME=qt5ct:qt6ct

# Only source this once
if [[ -z "$__HM_ZSH_SESS_VARS_SOURCED" ]]; then
  export __HM_ZSH_SESS_VARS_SOURCED=1

fi

export ZDOTDIR=$HOME/'.config/zsh'

export HISTCONTROL=ignoreboth:erasedups

export JAVA_HOME='/usr/lib/jvm/java-19-openjdk'
### PATH ###
# export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:$PATH"
if [ -d "$HOME/.bin" ] ;
  then PATH="$HOME/.bin:$PATH"
fi

if [ -d "$HOME/.local/bin" ] ;
  then PATH="$HOME/.local/bin:$PATH"
fi
export PATH="$PATH:$HOME/.local/share/bin"
export PATH="$PATH:$JAVA_HOME/bin:$HOME/.local/share/gem/ruby/3.0.0/bin:$HOME/Android/Sdk/platform-tools"
export PATH="$PATH:$HOME/.scripts"
# export PATH="$PATH:$HOME/.config/emacs/bin:$HOME/.emacs.d/bin"
export PATH="$PATH:/snap/bin"
export PATH="$PATH:$HOME/.local/share/JetBrains/Toolbox/scripts"
export PATH="$PATH:$HOME/.nimbel/bin"
export PATH="$PATH:/opt/xtensa-lx106-elf-gcc/bin"

### zoxide ###
export _ZO_ECHO=1

### cargo ###
export CARGO_TARGET_DIR=$HOME/.cargo-target
export CARGO_MOMMYS_LITTLE="boy/baby"
# export PATH="$PATH:$CARGO_TARGET_DIR/release"
# . "$HOME/.cargo/env"
if [ -d "$HOME/.cargo/bin" ]; then
    PATH="$PATH:$HOME/.cargo/bin"
fi
