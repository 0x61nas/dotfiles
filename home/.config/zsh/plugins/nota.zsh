: "${NOTA_FILE:=$HOME/.notas}"
: "${NOTA_ARCHIVE:=$HOME/.notas.archive}"
_NOTA_CACHED_NEXT_ID=1
_NOTA_FILE_LAST_TIMESTAMP=0

_nota_read_nextid() {
	if [[ -e "$NOTA_FILE" ]]; then
		local count_line=$(head -1 "$NOTA_FILE")
		_NOTA_CACHED_NEXT_ID=$(echo "$count_line" | grep -o '[0-9]\+')
	else
		_NOTA_CACHED_NEXT_ID=1
		{
			echo "NEXT_ID: 1"
			echo "@@@"
			echo
		} > "$NOTA_FILE"
	fi
}

_recache_nota_count() {
	local kurrent_timestamp=$(stat -c %Y "$NOTA_FILE")
	if [[ $_NOTA_FILE_LAST_TIMESTAMP -ne $kurrent_timestamp ]]; then
		_nota_read_nextid
		_NOTA_FILE_LAST_TIMESTAMP=kurrent_timestamp
	fi
}
_recache_nota_count

_nota_fzf_select() {
	# Extract notas in a format suitable for fzf (ID and Title)
  local notas=$(awk '
    /^#/ {
      id=$1; gsub(/[#:]/, "", id);  # Remove # and : from the ID
      title=$0; gsub(/^#[0-9]+: /, "", title);
      print id, title
    }
  ' "$NOTA_FILE")
  echo $(echo "$notas" | fzf --height=40% --layout=reverse --prompt="Select a nota: " \
    --preview="awk -v id={1} '
      /^#/ { in_nota_block=0 }
      \$0 ~ \"^#\" id \":\" { in_nota_block=1 }
      in_nota_block { print }
      /^---\$/ && in_nota_block { exit }
    ' \"$NOTA_FILE\"" | awk '{print $1}')
}

_nota_block_by_id() {
	awk -v id="$1" '
		/^.* @ .* #/ { in_nota_block=0 }
		$0 ~ "#" id ":" { in_nota_block=1 }
		in_nota_block { print }
		/^---$/ && in_nota_block { exit }
	' "$NOTA_FILE"
}

notaadd() {
	_recache_nota_count
  local title="$1"
	local description="$2"
	local autorun="$3"
	local _pwd="${4:-$(pwd)}"

	if [[ -z "$title" ]]; then
    echo -n "Enter the nota title: "
    read title
		if [[ -z "$title" ]]; then
			echo "The nota title can't be empty!" >/dev/stderr
			return true
		fi
  fi

  if [[ -z "$description" ]]; then
    echo -n "Enter the nota description (optional, press Enter to skip): "
    read description
  fi

	if [[ -z "$autorun" ]]; then
		echo -n "Enter the autorun cmd (optional): "
		read autorun
	fi

  # Generate the added date, nota_ID, and PWD
  local added_date=$(date '+%Y-%m-%d %H:%M')

  # Append the nota to the file
	local nota_id=$_NOTA_CACHED_NEXT_ID
  {
    echo "#$nota_id: $title @$added_date"
    [[ -n "$description" ]] && echo "+> $description"
    echo "~> $_pwd"
		[[ -n "$autorun" ]] && echo "\$> $autorun"
    echo '---'
		echo
  } >> "$NOTA_FILE"

	_NOTA_CACHED_NEXT_ID=$((nota_id + 1))
	sed -i "1s/NEXT_ID: [0-9]\+/NEXT_ID: $_NOTA_CACHED_NEXT_ID/" "$NOTA_FILE"
	_NOTA_FILE_LAST_TIMESTAMP=$(stat -c %Y "$NOTA_FILE")

  echo "Added nota #$nota_id: $title"
}

notalist() {
  if [[ ! -f "$NOTA_FILE" ]]; then
    echo "No notas found. Add one with 'notaadd'." >/dev/stderr
    return 1
  fi
	local selected_nota_id=$(_nota_fzf_select)

  if [[ -z "$selected_nota_id" ]]; then
    echo "No nota selected."
    return 0
  fi

  # Extract the PWD and command from the selected nota
  local selected_nota_pwd=$(awk -v id="$selected_nota_id" '
    /^#/ { in_nota_block=0 }
    $0 ~ "^#" id ":" { in_nota_block=1 }
    /^~> / && in_nota_block { print $2; exit }
  ' "$NOTA_FILE")

  local selected_nota_command=$(awk -v id="$selected_nota_id" '
    /^#/ { in_nota_block=0 }
    $0 ~ "^#" id ":" { in_nota_block=1 }
    /^\$> / && in_nota_block { $1=""; print $0; exit }
  ' "$NOTA_FILE")

  # Change to the selected PWD if it exists
  if [[ -n "$selected_nota_pwd" && -d "$selected_nota_pwd" ]]; then
    cd "$selected_nota_pwd"
    echo "~> $selected_nota_pwd"
  else
    echo "No valid PWD found for nota #$selected_nota_id."
  fi

  if [[ -n "$selected_nota_command" ]]; then
    echo "$>  $selected_nota_command"
    eval "$selected_nota_command"
  fi
}

notaedit() {
  if [[ ! -f "$NOTA_FILE" ]]; then
    echo "No notas found. Add one with 'notaadd'." >/dev/stderr
    return 1
  fi
  local nota_id="${1:-$(_nota_fzf_select)}"
  local temp_file=$(mktemp)

	_nota_block_by_id "$nota_id" > "$temp_file"

  # Check if the nota was found
  if [[ ! -s "$temp_file" ]]; then
    echo "Nota #$nota_id not found."
    rm "$temp_file"
    return 1
  fi

  # Get the original modification time of the temp file to use it as an indicator to the changes later
  local original_mtime=$(stat -c %Y "$temp_file")

  ${EDITOR:-vi} "$temp_file"

  # Check if the file was modified
  local updated_mtime=$(stat -c %Y "$temp_file")
  if [[ "$original_mtime" -eq "$updated_mtime" ]]; then
    echo "No changes made to nota #$nota_id."
    rm "$temp_file"
    return 0
  fi

  # Replace the nota block in the main file with the updated content
  awk -v id="$nota_id" -v temp_file="$temp_file" '
    BEGIN { while ((getline line < temp_file) > 0) updated_nota = updated_nota (updated_nota ? ORS : "") line }
    /^.* @ .* #/ { in_nota_block=0 }
    $0 ~ "#" id ":" { in_nota_block=1; print updated_nota; next }
    /^---$/ && in_nota_block { in_nota_block=0; next }
    !in_nota_block { print }
  ' "$NOTA_FILE" > "${NOTA_FILE}.tmp"

  # Replace the original file with the updated one
  mv "${NOTA_FILE}.tmp" "$NOTA_FILE"

  echo "Updated nota #$nota_id."
  rm "$temp_file"
}

notadone() {
  if [[ ! -f "$NOTA_FILE" ]]; then
    echo "No notas found. Add one with 'notaadd'." >/dev/stderr
    return 1
  fi

  local nota_id="${1:-$(_nota_fzf_select)}"
  if [[ -z "$nota_id" ]]; then
    echo "Usage: notadone <nota_id>"
    return 1
  fi
  if ! grep -E -q "^#$nota_id:" "$NOTA_FILE"; then
    echo "Nota #$nota_id not found."
    return 1
  fi

	_nota_block_by_id $nota_id >> "$NOTA_ARCHIVE"
  sed -i "/#$nota_id:/,/^---\$/d" "$NOTA_FILE"
  echo "Marked nota #$nota_id as done."
}


notahelp() {
  echo "Nota Manager Commands:"
  echo "  notaadd [title] [description] [autorun] - Add a new nota"
  echo "  notaedit [nota_id]  - Edit a nota by ID"
  echo "  notadone [nota_id] - Mark a nota as done by ID"
  echo "  notallist - List all notas with their IDs"
  echo "  notahelp - Show this help message"
}
