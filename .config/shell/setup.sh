PROMPT=ohmyposh
AURHELPER=paru
# Fix cava not showing bars
LC_MESSAGES=en_US.UTF-8
LANGUAGE=en_US
LANG=en_US.UTF-8

# Enable the autojump
[[ -s /etc/profile.d/autojump.sh ]] && source /etc/profile.d/autojump.sh
# Setup the github-copilot-cli alias `??`
if command -v github-copilot-cli >/dev/null 2>&1; then
  eval "$(github-copilot-cli alias -- "$0")"
fi

# The prompt
if command -v oh-my-posh >/dev/null 2>&1 && [[ $PROMPT == "ohmyposh" ]]; then
  eval "$(oh-my-posh init $(basename $SHELL) --config ~/.config/ohmyposh/1_shell.omp.json)"
fi
if command -v starship >/dev/null 2>&1 && [[ $PROMPT == "starship" ]]; then
  eval "$(starship init $(basename $SHELL))"
fi

if command -v opam >/dev/null 2>&1; then
  eval "$(opam env)"
fi



# Auto run
echo "Don't worry I'm here for you <3"
