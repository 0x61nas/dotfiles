# XDG
export XDG_CACHE_HOME=$HOME/.cache
export XDG_CONFIG_HOME=$HOME/.config
export XDG_DATA_HOME=$HOME/.local/share
export XDG_STATE_HOME=$HOME/.local/state

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
export PATH="$PATH:$HOME/.config/emacs/bin:$HOME/.emacs.d/bin"
export PATH="$PATH:/snap/bin"
export PATH="$PATH:$HOME/.local/share/JetBrains/Toolbox/scripts"

### cargo ###
export CARGO_TARGET_DIR=$HOME/.cargo-target
export PATH="$PATH:$CARGO_TARGET_DIR/release"
. "$HOME/.cargo/env"
