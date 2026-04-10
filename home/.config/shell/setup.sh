PROMPT=ohmyposh
AURHELPER=paru
# Fix cava not showing bars
LC_MESSAGES=en_US.UTF-8
LANGUAGE=en_US
LANG=en_US.UTF-8
SHELL_NAME=$(basename $SHELL)

[[ -e "$HOME/.private-env.sh" ]] && source "$HOME/.private-env.sh"

# if command -v gh >/dev/null 2>&1; then
#   eval "$(gh copilot alias -- $SHELL_NAME)"
# fi

# The prompt
# if command -v oh-my-posh >/dev/null 2>&1 && [[ $PROMPT == "ohmyposh" ]]; then
#   eval "$(oh-my-posh init $SHELL_NAME --config ~/.config/ohmyposh/1_shell.omp.json)"
# fi
# if command -v starship >/dev/null 2>&1 && [[ $PROMPT == "starship" ]]; then
#   eval "$(starship init $SHELL_NAME)"
# fi

# if command -v opam >/dev/null 2>&1; then
#   eval "$(opam env)"
# fi

if command -v intelli-shell >/dev/null 2>&1; then
	eval "$(intelli-shell init $SHELL_NAME)"
fi

# Auto run
echo "Don't worry I'm here for you <3"
