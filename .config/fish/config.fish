### EXPORT ###
set fish_greeting                                 # Supresses fish's intro message
set TERM "xterm-256color"                         # Sets the terminal type
set EDITOR "nvim"                                 # $EDITOR use nvim in terminal
set VISUAL "neovide"                              # $VISUAL use neovide in GUI mode

source $HOME/.config/fish/completions/*
source $HOME/.config/fish/functions/functions.fish # Loads the functions file
source $HOME/.config/shell/aliases.sh            # Loads the aliases file
clear
source $HOME/.config/nnn/config.sh

export GTK_IM_MODULE="fcitx"
export QT_IM_MODULE="fcitx"
export SDL_IM_MODULE="fcitx"
export XMODIFIERS="@im=fcitx"


### SET MANPAGER
### Uncomment only one of these!

### "bat" as manpager
set -x MANPAGER "sh -c 'col -bx | bat -l man -p'"

### "vim" as manpager
# set -x MANPAGER '/bin/bash -c "vim -MRn -c \"set buftype=nofile showtabline=0 ft=man ts=8 nomod nolist norelativenumber nonu noma\" -c \"normal L\" -c \"nmap q :qa<CR>\"</dev/tty <(col -b)"'

### "nvim" as manpager
# set -x MANPAGER "nvim -c 'set ft=man' -"

if status is-interactive
    # Commands to run in interactive sessions can go here
end

# Vi mode
function fish_user_key_bindings
  # fish_default_key_bindings
  fish_vi_key_bindings
end

### AUTOCOMPLETE AND HIGHLIGHT COLORS ###
set fish_color_normal brcyan
set fish_color_autosuggestion '#7d7d7d'
set fish_color_command brcyan
set fish_color_error '#ff6c6b'
set fish_color_param brcyan

### SETTING THE STARSHIP PROMPT ###
# starship init fish | source
thefuck --alias | source

# pnpm
set -gx PNPM_HOME "/home/anas/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end

# Auto run
echo "Don't worry I'm here for you <3"
oh-my-posh init fish --config ~/.config/ohmyposh/1_shell.omp.json | source


