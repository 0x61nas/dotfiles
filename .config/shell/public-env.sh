export BROWSER='firefox-developer-edition'
# ls colors from https://github.com/body20002/nova/blob/main/nova.zsh-theme + *.jar and *.mp4, *.mkv from me :D
export LS_COLORS='no=00:fi=00:di=01;34:ln=00;36:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=41;33;01:ex=00;32:*.cmd=00;32:*.jar=01;32:*.com=01;32:*.bat=01;32:*.btm=01;32:*.dll=01;32:*.tar=00;31:*.tbz=00;31:*.tgz=00;31:*.rpm=00;31:*.deb=00;31:*.arj=00;31:*.taz=00;31:*.lzh=00;31:*.lzma=00;31:*.zip=00;31:*.zoo=00;31:*.z=00;31:*.Z=00;31:*.gz=00;31:*.bz2=00;31:*.tb2=00;31:*.tz2=00;31:*.tbz2=00;31:*.avi=01;35:*.bmp=01;35:*.fli=01;35:*.gif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mng=01;35:*.mov=01;35:*.mpg=01;35:*.mp4=01;35:*.mkv=01;35:*.pcx=01;35:*.pbm=01;35:*.pgm=01;35:*.png=01;35:*.ppm=01;35:*.tga=01;35:*.tif=01;35:*.xbm=01;35:*.xpm=01;35:*.dl=01;35:*.gl=01;35:*.wmv=01;35:*.aiff=00;32:*.au=00;32:*.mid=00;32:*.mp3=00;32:*.ogg=00;32:*.voc=00;32:*.wav=00;32:'

# XDG
export XDG_CACHE_HOME=$HOME/.cache
export XDG_CONFIG_HOME=$HOME/.config
export XDG_DATA_HOME=$HOME/.local/share
export XDG_STATE_HOME=$HOME/.local/state

# Editor
export EDITOR='lvim'
export VISUAL="lvim"

export HISTCONTROL=ignoreboth:erasedups
export PAGER='bat'

export JAVA_HOME='/usr/lib/jvm/java-19-openjdk'
### PATH ###
# export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:$PATH"
if [ -d "$HOME/.bin" ] ;
  then PATH="$HOME/.bin:$PATH"
fi

if [ -d "$HOME/.local/bin" ] ;
  then PATH="$HOME/.local/bin:$PATH"
fi

export PATH="$JAVA_HOME/bin:$HOME/.local/share/gem/ruby/3.0.0/bin:$HOME/Android/Sdk/platform-tools:$PATH"
export PATH="$HOME/.scripts:$PATH"
export PATH="$HOME/.config/emacs/bin:$HOME/.emacs.d/bin:$PATH"
export PATH="/snap/bin:$PATH"
export PATH="$HOME/.cargo/bin:$PATH"
