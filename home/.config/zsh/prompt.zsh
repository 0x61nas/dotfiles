function shrink_path {
    # Replace the home directory with ~ for brevity
    local path="${PWD/#$HOME/~}"
    local new_path=""
    local -a path_components=("${(@s:/:)path}")
    local num_components=${#path_components[@]}
    # Loop through each component except the last one
    for (( i=1; i < num_components; i++ )); do
        if [[ -n ${path_components[i]} ]]; then
            new_path+="%{$fg[yellow]%}${path_components[i][1]}%{$reset_color%}%{$fg[white]%}:%{$reset_color%}"
        fi
    done
    # Add the last directory in full (without a trailing slash)
    local last_part=""
    if (( num_components > 1 )); then
        last_part="${path_components[-1]}"
    else
        # If there's only one component, it gets added in full
        last_part="${path_components[1]}"
    fi
    new_path+="%{$fg[yellow]%}${last_part}%{$reset_color%}%"
    echo "$new_path"
}

# Set cursor style (DECSCUSR), VT520.
# 0  ⇒  blinking block.
# 1  ⇒  blinking block (default).
# 2  ⇒  steady block.
# 3  ⇒  blinking underline.
# 4  ⇒  steady underline.
# 5  ⇒  blinking bar, xterm.
# 6  ⇒  steady bar, xterm.
_fix_cursor() {
   local cursor=3
   if [[ -n $CURSOR_SHAPE ]]; then
       cursor=$CURSOR_SHAPE
   fi
   echo -ne "\e[$cursor q"
}

function _update_prompt {
	# PROMPT="[ $(shrink_path)  ]%(!.#.$) "
	export PS1="[ $(shrink_path)  ]<%?>%(!.#.$) "
}

autoload -Uz add-zsh-hook
add-zsh-hook chpwd _update_prompt
add-zsh-hook precmd _fix_cursor

_update_prompt
