NEKOJUMB_DATABASE="${NEKOJUMB_DATABASE:-$HOME/.nekojump_database}"
__NEKOJUMB_MAX_SCORE=10000
__NEKOJUMB_DATABASE_VERSION=1

_nekojump_init_db() {
    [[ -f "$1" ]] || \print "VERSION: $__NEKOJUMB_DATABASE_VERSION" > "$1"
}

_nekojump_fail() {
    \print -P "%F{red}nekojump: $1%f" >&2
}

_nekojump_warn() {
    \print -P "%F{yellow}nekojump: $1%f" >&2
}

_nekojump_success() {
    \print -P "%F{green}nekojump: $1%f"
}

_nekojump_check_db_compat() {
    local db="$1"
    [[ -f "$db" ]] || return 0
    local db_version
    db_version="$(\head -n 1 "$db" 2>/dev/null)"
    [[ "$db_version" == "VERSION: $__NEKOJUMB_DATABASE_VERSION" ]] && return 0
    _nekojump_fail "incompatible database version in $db (found: $db_version, expected: VERSION: $__NEKOJUMB_DATABASE_VERSION)"
    return 1
}

_nekojump_track() {
    local db="$NEKOJUMB_DATABASE"
    local temp_db="${db}.$$"
    local now="$(date +%s)"
    local target="$PWD"

    _nekojump_init_db "$db"
    _nekojump_check_db_compat "$db" || return 1

    _nekojump_init_db "$temp_db"
    \awk -F '|' -v now="$now" -v target="$target" -v max="$__NEKOJUMB_MAX_SCORE" '
    BEGIN { found = 0 }
    NR>1 {
        score = $1; path = $2; ts = $3
        days = (now - ts) / 86400
        if (days > 0) score = score * (0.9 ^ days)
        
        if (path == target) {
            score += 1
            ts = now
            found = 1
        }
        
        if (score > max) score = max
        if (score >= 0.01) printf "%.3f|%s|%s\n", score, path, ts
    }
    END {
        if (!found) printf "1.000|%s|%s\n", target, now
    }' "$db" >> "$temp_db" && \mv -f "$temp_db" "$db"
}

nekojump() {
    local query="$*"
    
    if [[ -d "$query" ]]; then
        \cd "$query"
        return 0
    elif [[ -f "$query" ]]; then
        \cd "${query:h}"
        return 0
    fi

    local parent="$PWD"
    local lower_query="${(L)query}"
    while [[ "$parent" != "/" && "$parent" != "." ]]; do
        parent="${parent:h}"
        if [[ "${(L)parent:t}" == *"$lower_query"* ]]; then
            \cd "$parent"
            return 0
        fi
        [[ "$parent" == "/" ]] && break
    done

    local db="$NEKOJUMB_DATABASE"
    [[ -f "$db" ]] || {
        _nekojump_fail "the NekoJump database doesn't exist yet"
        _nekojump_warn "falling back to standard cd (try visiting some directories first!)"
        \cd "$query"
        return $?
    }

    _nekojump_check_db_compat "$db" || {
        _nekojump_warn "database format incompatible, falling back to standard cd"
        \cd "$query"
        return $?
    }

    local match
    match=$(
      \awk -F'|' -v q="$query" -v c="$PWD" '
        BEGIN {
          IGNORECASE=1
          best_score = -1
          best = ""
          best_exact = ""
          best_exact_from_name = 0
        }
        NR > 1 {
          score = $1 + 0
          path  = $2

          if (path == c) next

          name = path
          sub(/^.*\//, "", name)

          if (tolower(name) == tolower(q)) {
            if (!best_exact_from_name || score > best_score) {
              best_exact_from_name = 1
              best_score = score
              best_exact = path
            }
            next
          }

          if (index(tolower(path), tolower(q)) && score > best_score) {
            best_score = score
            best = path
          }
        }
        END {
          if (best_exact != "") print best_exact
          else if (best != "") print best
        }
      ' "$db" 2>/dev/null
    )
    
    if [[ -z "$match" ]]; then
        _nekojump_fail "No match found for '$1'"
        return 1
    fi

    # Handle case where matched path is a file (unlikely but safe)
    if [[ -f "$match" ]]; then
        _nekojump_warn 'the match is a file, using the parent'
        match="${match:h}"
    fi

    if [[ -d "$match" ]]; then
        \cd "$match"
    else
        _nekojump_fail "match exists in DB but directory is missing: $match"
        # TODO(anas): Clean up here automatically?
        return 1
    fi
}

nekojumpi() {
    command -v fzf >/dev/null || return 69
    local db="$NEKOJUMB_DATABASE"
    [[ -f "$db" ]] || return 1
    _nekojump_check_db_compat "$db" || return 1
    local dest
    if [[ -z "$1" ]]; then
        dest="$(\tail --lines=+2 "$db" | \sort -t '|' -k1 -nr | \cut -d '|' -f 2 | \fzf)"
    else
        dest="$(\tail --lines=+2 "$db" | \grep "$1" | \sort -t '|' -k1 -nr | \cut -d '|' -f 2 | \fzf)"
    fi
    [[ -n "$dest" ]] && \cd "$dest"
}

nekojumpd() {
    local db="$NEKOJUMB_DATABASE"
    local temp_db="${db}.$$"
    local target="${1:-$PWD}"
    _nekojump_init_db "$temp_db"
    _nekojump_check_db_compat "$db" || return 1
    \awk -F '|' -v target="$target" 'NR>1 && $2 != target' "$db" >> "$temp_db" && \mv -f "$temp_db" "$db"
}

nekojumpclean() {
    local db="$NEKOJUMB_DATABASE"
    local temp_db="${db}.$$"
    _nekojump_init_db "$temp_db"
    _nekojump_check_db_compat "$db" || return 1
    local count_before=$(($(\wc -l < "$db") - 1))
    \awk -F '|' '{
        if (system("test -d \"" $2 "\"") == 0) print $0
    }' "$db" >> "$temp_db" && \mv -f "$temp_db" "$db"
    local count_after=$(($(\wc -l < "$db") - 1))
    local removed=$((count_before - count_after))
    if [[ $removed -gt 0 ]]; then
        _nekojump_success "cleaned up $removed dead directory entry/entries"
    else
        _nekojump_success "database is already clean"
    fi
}

nekojumptop() {
    local db="$NEKOJUMB_DATABASE"
    [[ -f "$db" ]] || {
        _nekojump_fail "database doesn't exist yet"
        return 1
    }
    _nekojump_check_db_compat "$db" || return 1
    local count="${1:-10}"
    _nekojump_success "Top $count most visited directories:"
 while IFS='|' read -r _nekojump_score _nekojump_path; do
        printf '  %.1f\t\t%s\n' "$_nekojump_score" "$_nekojump_path"
    done < <(\tail --lines=+2 "$db" | \sort -t '|' -k1 -nr | \head -n "$count" | \cut -d '|' -f 2,1)
}

nekojumpstats() {
    local db="$NEKOJUMB_DATABASE"
    [[ -f "$db" ]] || {
        _nekojump_fail "database doesn't exist yet"
        return 1
    }
    _nekojump_check_db_compat "$db" || return 1
    local total=$(($(\wc -l < "$db") - 1))
    _nekojump_success "Database stats:"
    printf '  Total directories tracked: %d\n' "$total"
    printf '  Database location: %s\n' "$db"
    printf '  Database size: %s\n' "$(\du -h "$db" | \cut -f1)"
}

autoload -Uz add-zsh-hook
add-zsh-hook chpwd _nekojump_track
[[ ! -f "$NEKOJUMB_DATABASE" ]] && _nekojump_init_db "$NEKOJUMB_DATABASE"
alias z='nekojump'
alias zi='nekojumpi'
alias zd='nekojumpd'
alias zcl='nekojumpclean'
alias ztop='nekojumptop'
alias zstats='nekojumpstats'
