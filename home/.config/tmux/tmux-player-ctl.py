#!/usr/bin/env python3
import unicodedata
"""
tmux-player-ctl - A tmux popup controller for MPRIS media players via playerctl.

Usage:
    tmux display-popup -x0 -y0 -w100% -h100% -E "python3 /path/to/tmux-player-ctl.py"
"""

from concurrent.futures import ThreadPoolExecutor

import os
import sys
import signal
import atexit
import subprocess
import select
import time
import re
import shutil
from dataclasses import dataclass
from typing import Optional, List


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────


class Config:
    UI_WIDTH = 72  # Width of the UI box
    INNER_W = UI_WIDTH - 4  # Content area width (excluding borders and padding)
    SEEK_SECONDS = 10


def detect_terminal_width() -> int:
    """Detect terminal width, preferring tmux pane width when available."""
    # Check if we're in tmux
    if os.environ.get("TMUX_PANE"):
        try:
            result = subprocess.run(
                ["tmux", "display-message", "-p", "#{pane_width}"],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0:
                width = int(result.stdout.strip())
                if width > 0:
                    return width
        except (ValueError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    # Fallback to shutil
    return shutil.get_terminal_size().columns


def detect_and_apply_terminal_width():
    """Detect terminal width and clamp Config.UI_WIDTH to max 72."""
    terminal_width = detect_terminal_width()
    Config.UI_WIDTH = min(72, terminal_width)
    Config.INNER_W = Config.UI_WIDTH - 4


_playerctl_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pctl")

# ─────────────────────────────────────────────────────────────────────────────
# Icons
# ─────────────────────────────────────────────────────────────────────────────

# Unicode symbols (VS15 \uFE0E for text presentation)
ICONS = {
    # Status
    "playing": "\u23f5\ufe0e",  # ▶
    "recording": "\u23fa\ufe0e ",  # ⏺
    "paused": "\u23f8\ufe0e ",  # ⏸
    "stopped": "\u25a0\ufe0e",  # ■
    "play-pause": "\u23ef\ufe0e",  # ⏯
    # Navigation
    "tab": "\u21e5\ufe0e",  # ⇥ tab
    "prev": "\u25c0\ufe0e",  # ◀
    "seek-left": "\u23ea\ufe0e",  # ⏪
    "seek-right": "\u23e9\ufe0e",  # ⏩
    "next": "\u23ed\ufe0e",  # ⏭
    "skip-start": "\u23ee\ufe0e",  # ⏮
    "skip-end": "\u23ed\ufe0e",  # ⏭ (same as next)
    "eject": "\u23cf\ufe0e",  # ⏏
    # Volume
    "vol-muted": "\U0001f507",  # 🔇
    "vol-low": "\U0001f508",  # 🔈
    "vol-med": "\U0001f509",  # 🔉
    "vol-high": "\U0001f50a",  # 🔊
    # Playlist
    "shuffle": "\U0001f500\ufe0e",  # 🔀
    "repeat": "\U0001f501\ufe0e",  # 🔁
    "repeat-one": "\U0001f502\ufe0e",  # 🔂
    # Tools
    "seek": '←→',
    "vol-change": '↑↓',
    "toggle-play": '␣',
}


def icon(name: str) -> str:
    """Return the raw icon symbol."""
    return ICONS.get(name, "?")


# ─────────────────────────────────────────────────────────────────────────────
# Icon lookups
# ─────────────────────────────────────────────────────────────────────────────

VOL_ICONS = {
    0: "vol-muted",
    (1, 32): "vol-low",
    (33, 65): "vol-med",
    (66, 100): "vol-high",
}


# ─────────────────────────────────────────────────────────────────────────────
# Color helpers
# ─────────────────────────────────────────────────────────────────────────────


def colorize(text: str, color: str) -> str:
    """Add ANSI color to text, then reset."""
    return f"{color}{text}{Theme.RESET}"


# ─────────────────────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PlayerState:
    player: str = ""
    status: str = ""
    title: str = ""
    artist: str = ""
    album: str = ""
    position: float = 0.0
    length: float = 0.0
    volume: int = 0
    loop: str = "None"
    shuffle: str = "false"
    dirty: bool = True
    pre_mute_volume: int = 50  # Store volume before mute for restore on unmute
    _start_time_w: Optional[int] = (
        None  # Width of start time (set by progress_row for volume_row)
    )
    _end_time_w: Optional[int] = (
        None  # Width of end time (set by progress_row for volume_row)
    )
    trackNumber: str = ""  # Current track number
    trackCount: int = 0  # Total tracks in album


class PlayerTracker:
    """Holds all player-related global state. Single instance 's' at module level."""

    current_player: str = ""
    available_players: List[str] = []
    current_player_idx: int = -1
    state: "PlayerState" = None  # type: ignore[assignment]
    last_command_time: float = 0.0
    meta_proc: Optional["subprocess.Popen"] = None

    def __init__(self) -> None:
        self.state = PlayerState()


s = PlayerTracker()


# Ordered field names (39 fields, matching METADATA_FORMAT)
METADATA_FIELDS = [
    "player",
    "status",
    "title",
    "artist",
    "album",
    "albumArtist",
    "trackNumber",
    "trackCount",
    "discNumber",
    "genre",
    "explicit",
    "subtitle",
    "asText",
    "composer",
    "lyricist",
    "conductor",
    "performer",
    "arranger",
    "releaseDate",
    "contentCreated",
    "musicBrainzTrackId",
    "musicBrainzAlbumId",
    "musicBrainzArtistIds",
    "comment",
    "mood",
    "url",
    "userHomePage",
    "useCount",
    "autoRating",
    "audioBPM",
    "language",
    "lyrics",
    "position",
    "length",
    "volume",
    "loopStatus",
    "loop",
    "shuffle",
    "artUrl",
    "trackid",
]

# Playerctl field names in same order as METADATA_FIELDS
_METADATA_KEYS = [
    "{{playerName}}",
    "{{status}}",
    "{{title}}",
    "{{artist}}",
    "{{album}}",
    "{{albumArtist}}",
    "{{xesam:trackNumber}}",
    "{{xesam:trackCount}}",
    "{{discNumber}}",
    "{{genre}}",
    "{{xesam:explicit}}",
    "{{subtitle}}",
    "{{asText}}",
    "{{composer}}",
    "{{lyricist}}",
    "{{conductor}}",
    "{{performer}}",
    "{{arranger}}",
    "{{releaseDate}}",
    "{{contentCreated}}",
    "{{musicBrainzTrackId}}",
    "{{musicBrainzAlbumId}}",
    "{{musicBrainzArtistIds}}",
    "{{comment}}",
    "{{mood}}",
    "{{url}}",
    "{{userHomePage}}",
    "{{useCount}}",
    "{{autoRating}}",
    "{{audioBPM}}",
    "{{language}}",
    "{{lyrics}}",
    "{{position}}",
    "{{mpris:length}}",
    "{{volume}}",
    "{{loopStatus}}",
    "{{loop}}",
    "{{shuffle}}",
    "{{mpris:artUrl}}",
    "{{mpris:trackid}}",
]
# Prefixed format: \n@0@{{playerName}}\n@1@{{status}}\n... for robust framing
METADATA_FORMAT = "\n" + "\n".join(
    f"@{i}@{key}" for i, key in enumerate(_METADATA_KEYS)
)

# Debounce follower updates after commands (in seconds)
COMMAND_DEBOUNCE = 0.3
COMMAND_COOLDOWN = 0.05  # Minimum time between async calls

# ─────────────────────────────────────────────────────────────────────────────
# Shutdown handling
# ─────────────────────────────────────────────────────────────────────────────

shutdown_requested = False


def request_shutdown(signum, frame=None):
    global shutdown_requested
    shutdown_requested = True


def setup_signals():
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, request_shutdown)
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, request_shutdown)
    if hasattr(signal, "SIGQUIT"):
        signal.signal(signal.SIGQUIT, request_shutdown)
    atexit.register(cleanup)


# ─────────────────────────────────────────────────────────────────────────────
# Process management
# ─────────────────────────────────────────────────────────────────────────────

processes: list[subprocess.Popen] = []


def cleanup():
    _playerctl_pool.shutdown(wait=False)
    for proc in list(processes):
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    proc.wait(timeout=0.5)
                except OSError:
                    pass
    processes.clear()


def cleanup_proc(proc: Optional[subprocess.Popen]) -> None:
    if not proc:
        return
    try:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=0.5)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=0.5)
        except (subprocess.TimeoutExpired, OSError):
            pass
    except OSError:
        pass
    if proc in processes:
        processes.remove(proc)


# ─────────────────────────────────────────────────────────────────────────────
# UI Rendering
# ─────────────────────────────────────────────────────────────────────────────


def render_ui():
    """Render the full UI to stdout."""
    global s
    # Build all rows
    rows = [
        border_top(),
        header_row(),
        border_mid(),
        album_row(),
        track_row(),
        artist_row(),
        border_mid(),
        progress_row(),
        volume_row(),
        border_mid(),
        toolbar_row(),
        border_bot(),
    ]

    # Write all lines with explicit cursor positioning (no newlines)
    for i, line in enumerate(rows):
        move_cursor(1 + i, 1)
        sys.stdout.write(line)

    sys.stdout.flush()
    s.state.dirty = False


# ─────────────────────────────────────────────────────────────────────────────


def get_available_players() -> List[str]:
    """List all available MPRIS players. Does NOT use player_args (no -p flag)."""
    try:
        result = subprocess.run(
            ["playerctl", "--list-all"],
            capture_output=True, text=True, timeout=1,
        )
        if result.returncode != 0:
            return []
        return [p.strip() for p in result.stdout.strip().split("\n") if p.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def check_playerctl() -> None:
    """Verify playerctl command exists. Exits with error if not."""
    result = _playerctl_subprocess(["--version"], timeout=1)
    if result.returncode != 0:
        print("Error: playerctl command not available", file=sys.stderr)
        sys.exit(1)


def get_best_player(players: List[str]) -> Optional[str]:
    """Select best player: Playing > Paused > first available."""
    if not players:
        return None
    global s
    for player in players:
        prev, s.current_player = s.current_player, player
        status = run_playerctl("status")
        s.current_player = prev
        if status and status.strip() == "Playing":
            return player
    for player in players:
        prev, s.current_player = s.current_player, player
        status = run_playerctl("status")
        s.current_player = prev
        if status and status.strip() == "Paused":
            return player
    return players[0]


def _playerctl_subprocess(
    extra_args: Optional[List[str]] = None,
    timeout: float = 0.5,
    capture: bool = True,
) -> subprocess.CompletedProcess:
    """Spawn playerctl subprocess. All subprocess.run calls go through here."""
    args = ["playerctl"] + player_args() + (list(extra_args) if extra_args else [])
    try:
        stdout = subprocess.PIPE if capture else subprocess.DEVNULL
        stderr = subprocess.PIPE if capture else subprocess.DEVNULL
        return subprocess.run(args, stdout=stdout, stderr=stderr, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return subprocess.CompletedProcess(args, 1, "", "")


def player_args() -> List[str]:
    global s
    return ["-p", s.current_player] if s.current_player else []


def reset_state():
    """Reset all state fields with a fresh PlayerState."""
    global s
    s.state = PlayerState()
    s.state.status = "No player"  # Override default "" with explicit no-player message


def switch_player() -> Optional[subprocess.Popen]:
    """Switch to next player. Returns new metadata follower process."""
    global s

    cleanup_proc(s.meta_proc)

    s.available_players = get_available_players()
    if not s.available_players:
        reset_state()
        s.current_player = ""
        s.current_player_idx = -1
        s.meta_proc = None
        return None

    # Handle case where previous player is no longer available
    if s.current_player not in s.available_players:
        s.current_player_idx = 0
    else:
        s.current_player_idx = (s.current_player_idx + 1) % len(s.available_players)
    s.current_player = s.available_players[s.current_player_idx]

    # Reset state so stale metadata from previous player doesn't linger
    reset_state()
    s.state.player = s.current_player
    # Query shuffle and loop state (not in metadata follower)
    s.state.shuffle = run_playerctl("shuffle").strip() or "false"
    s.state.loop = run_playerctl("loop").strip() or "None"

    s.meta_proc = start_metadata_follower()

    if s.meta_proc is None:
        return None

    result = run_playerctl("--format", METADATA_FORMAT, "metadata")
    if result:
        data = parse_metadata(result)
        update_state_from_metadata(data)
    else:
        s.state.status = "Stopped"
        s.state.dirty = True

    return s.meta_proc


def run_playerctl(*args) -> str:
    """Run playerctl command, return stdout stripped."""
    result = _playerctl_subprocess(list(args))
    if result.returncode != 0:
        return ""
    return result.stdout


def start_metadata_follower() -> Optional[subprocess.Popen]:
    """Start background metadata follower."""
    try:
        proc = subprocess.Popen(
            ["playerctl"]
            + player_args()
            + ["--format", METADATA_FORMAT, "--follow", "metadata"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        processes.append(proc)
        return proc
    except OSError:
        return None


def _parse_volume(raw: str) -> int:
    """Convert volume float (0.0-1.0) to int (0-100)."""
    if not raw:
        return 0
    try:
        vol = float(raw)
        vol = max(0.0, min(1.0, vol))  # clamp
        return round(vol * 100)
    except (ValueError, TypeError):
        return 0


def parse_metadata(raw: str) -> dict:
    """Parse prefixed metadata. Fields are \n@0@value\n@1@value\n...

    Newlines within field values are preserved since we split on \n@N@ pattern.
    """
    try:
        parts = raw.split("\n@")
        # parts[0] is empty string (before leading \n)
        data: dict[str, str] = {}
        for part in parts[1:]:
            end = part.index("@")
            idx = int(part[:end])
            if 0 <= idx < len(METADATA_FIELDS):
                data[METADATA_FIELDS[idx]] = part[end + 1 :]
    except (ValueError, IndexError):
        return {}

    def get(key: str, default: str = "") -> str:
        return data.get(key, default)

    try:
        return {
            # Basic info
            "player": get("player"),
            "status": get("status"),
            "title": get("title"),
            "artist": get("artist"),
            "album": get("album"),
            # Track details
            "albumArtist": get("albumArtist"),
            "trackNumber": get("trackNumber"),
            "trackCount": int(get("trackCount")) if get("trackCount") else 0,
            "discNumber": get("discNumber"),
            "genre": get("genre"),
            "explicit": get("explicit", "false"),
            "subtitle": get("subtitle"),
            "asText": get("asText"),
            # People
            "composer": get("composer"),
            "lyricist": get("lyricist"),
            "conductor": get("conductor"),
            "performer": get("performer"),
            "arranger": get("arranger"),
            # Dates & IDs
            "releaseDate": get("releaseDate"),
            "contentCreated": get("contentCreated"),
            "musicBrainzTrackId": get("musicBrainzTrackId"),
            "musicBrainzAlbumId": get("musicBrainzAlbumId"),
            "musicBrainzArtistIds": get("musicBrainzArtistIds"),
            # Other
            "comment": get("comment"),
            "mood": get("mood"),
            "url": get("url"),
            "userHomePage": get("userHomePage"),
            "useCount": get("useCount"),
            "autoRating": get("autoRating"),
            "audioBPM": get("audioBPM"),
            "language": get("language"),
            "lyrics": get("lyrics"),
            # Playback
            "position": float(data["position"]) / 1_000_000 if data.get("position") else 0.0,
            "length": float(data["length"]) / 1_000_000 if data.get("length") else 0.0,
            "volume": _parse_volume(get("volume")),
            "loopStatus": get("loopStatus", "None"),
            "loop": get("loop", "None"),
            "shuffle": get("shuffle", "false"),
            # Extra
            "artUrl": get("artUrl"),
            "trackid": get("trackid"),
        }
    except (ValueError, KeyError):
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Theme Configuration
# ─────────────────────────────────────────────────────────────────────────────


class Theme:
    # Catppuccin Mocha palette (24-bit RGB: \033[38;2;R;G;Bm)

    # Background: 24-bit RGB like "0;0;0" for black
    BG = os.environ.get("TPCTL_BG", "")

    # Status colors
    PLAYING = os.environ.get("TPCTL_PLAYING", "\033[38;2;166;227;161m")  # green
    PAUSED = os.environ.get("TPCTL_PAUSED", "\033[38;2;249;226;175m")  # yellow
    STOPPED = os.environ.get("TPCTL_STOPPED", "\033[38;2;108;112;134m")  # overlay0
    RECORDING = os.environ.get("TPCTL_RECORDING", "\033[38;2;243;139;168m")  # red

    # Key hints
    KEY_HINT = os.environ.get("TPCTL_KEY_HINT", "\033[38;2;137;180;250m")  # blue

    # Borders & labels
    BORDER = os.environ.get("TPCTL_BORDER", "\033[38;2;108;112;134m")  # overlay0
    DIM = os.environ.get("TPCTL_DIM", "\033[38;2;108;112;134m")  # overlay0

    # Progress bar
    PROGRESS_FILL = os.environ.get(
        "TPCTL_PROGRESS_FILL", "\033[38;2;137;180;250m"
    )  # blue
    PROGRESS_EMPTY = os.environ.get(
        "TPCTL_PROGRESS_EMPTY", "\033[38;2;108;112;134m"
    )  # overlay0

    # Volume bar (VU meter gradient: green → yellow → red)
    # Low=green, Med=yellow, High=red, Empty=dimmed
    VOL_MUTED = os.environ.get("TPCTL_VOL_MUTED", "\033[38;2;243;139;168m")  # red
    VOL_LOW = os.environ.get("TPCTL_VOL_LOW", "\033[38;2;166;227;161m")  # green
    VOL_MED = os.environ.get("TPCTL_VOL_MED", "\033[38;2;249;226;175m")  # yellow
    VOL_HIGH = os.environ.get("TPCTL_VOL_HIGH", "\033[38;2;243;139;168m")  # red
    VOL_EMPTY = os.environ.get("TPCTL_VOL_EMPTY", "\033[38;2;17;17;27m")  # dark base

    # Reset includes background color so it's reapplied after each reset
    RESET = f"\033[0m{'' if not BG else f'\033[48;2;{BG}m'}"


def status_color(status: str) -> str:
    """Get color for status."""
    colors = {
        "Playing": Theme.PLAYING,
        "Paused": Theme.PAUSED,
        "Stopped": Theme.STOPPED,
        "Recording": Theme.RECORDING,
    }
    return colors.get(status, Theme.STOPPED)


# ─────────────────────────────────────────────────────────────────────────────
# UI Row Builders
# ─────────────────────────────────────────────────────────────────────────────


def border_top() -> str:
    """Top border: ┌ followed by ─ repeated, then ┐"""
    return f"{Theme.BORDER}┌{'─' * (Config.UI_WIDTH - 2)}┐{Theme.RESET}"


def border_mid() -> str:
    """Middle border: ├ followed by ─ repeated, then ┤"""
    return f"{Theme.BORDER}├{'─' * (Config.UI_WIDTH - 2)}┤{Theme.RESET}"


def border_bot() -> str:
    """Bottom border: └ followed by ─ repeated, then ┘"""
    return f"{Theme.BORDER}└{'─' * (Config.UI_WIDTH - 2)}┘{Theme.RESET}"


def _status_icon(status: str) -> str:
    """Get icon name for status (lowercase)."""
    return status.lower()


def _format_player_name(player: str) -> str:
    """Format player name: strip .instanceN suffix."""
    if not player:
        return ""
    if ".instance" in player:
        return player.split(".instance")[0]
    return player


def header_row() -> str:
    """Header row with status, player name, and switch."""
    global s
    status_w = 20  # 1 icon + space + max status "No MPRIS player" (18 chars)
    switch_w = 9  # 1 icon + space + 6 "switch" + 1 padding
    player_w = Config.INNER_W - status_w - switch_w - 2  # 2 for the gaps between slots

    status_icon = icon(_status_icon(s.state.status))
    status_text = colorize(
        f"{status_icon} {s.state.status.lower()}", status_color(s.state.status)
    )

    player_name = f" {truncate(_format_player_name(s.state.player), player_w - 2)} "

    if len(s.available_players) > 1:
        switch_text = f"{colorize(icon('tab'), Theme.KEY_HINT)} switch"
    else:
        switch_text = ""

    return row(
        (status_text, status_w, "<"),
        (player_name, player_w, "^"),
        (switch_text, switch_w, ">"),
    )


def _info_row(label: str, value: str):
    """Info row: label (7) + value (remaining)."""
    lw, gap = 7, 1
    vw = Config.INNER_W - lw - gap
    label_colored = colorize(f"{label:>{lw}}", Theme.DIM)
    value_text = truncate(value, vw)
    return row(
        (label_colored, lw, ">"),
        (value_text, vw, "<"),
    )


def _calc_track_num_width(track_count: int) -> int:
    """Calculate the width needed for track number display.

    Format: "X / Y" where X is track number and Y is total count.
    Handles track counts up to 9999 tracks (4 digits).
    """
    if track_count <= 0:
        return 0
    # Width of the count portion: max of track number and track count digits
    # plus 3 for " / " separator
    count_digits = max(len(str(track_count)), 1)
    return count_digits + 3 + count_digits  # "X / Y" format

def _artist_row_slots(artist: str, shuffle: str, loop: str):
    """Build artist row slots: label (7) + artist (flex) + shuffle/loop indicators.

    Shuffle: icon + " shuf" when ON, "shuf" when OFF (s highlighted, rest dimmed)
    Loop: icon + " loop" when ON, "loop" when OFF (l highlighted, rest dimmed)
    """
    lw, gap = 7, 1

    # Build shuffle/loop slot on the right
    sl_parts = []
    sl_width = 0

    # Shuffle: icon + "shuf" when ON, "shuf" when OFF
    if shuffle == "true":
        shuffle_icon = icon("shuffle")
        # ON: "s" highlighted, "huf" bright
        shuffle_text = f"{colorize('s', Theme.KEY_HINT)}huf"
        sl_parts.append(f"{shuffle_icon} {shuffle_text}")
        sl_width += visible_width(shuffle_icon) + 1 + 5  # icon + space + "shuf"
    else:
        # OFF: "shuf" without icon (s highlighted, rest dimmed)
        shuffle_text = f"{colorize('s', Theme.KEY_HINT)}{colorize('huf', Theme.DIM)}"
        sl_parts.append(shuffle_text)
        sl_width += 5  # "shuf"

    # Loop: icon + "loop" when ON, "loop" when OFF
    if loop in ("Track", "Playlist"):
        loop_icon = icon("repeat-one") if loop == "Track" else icon("repeat")
        # ON: "l" highlighted, "oop" bright
        loop_text = f"{colorize('l', Theme.KEY_HINT)}oop"
        sl_parts.append(f"{loop_icon} {loop_text}")
        sl_width += visible_width(loop_icon) + 1 + 4  # icon + space + "loop"
    elif loop == "None":
        # OFF: "loop" without icon (l highlighted, rest dimmed)
        loop_text = f"{colorize('l', Theme.KEY_HINT)}{colorize('oop', Theme.DIM)}"
        sl_parts.append(loop_text)
        sl_width += 4  # "loop"

    # Total width for shuffle/loop slot
    sl_slot_w = sl_width

    # Artist name width: inner - label - gap - shuffle/loop - gap
    aw = Config.INNER_W - lw - gap - sl_slot_w - gap

    # Truncate artist name if needed
    artist_text = truncate(artist, aw) if aw > 0 else ""
    label_colored = colorize(f"{'Artist:':>{lw}}", Theme.DIM)

    slots = [
        (label_colored, lw, ">"),
        (artist_text, aw, "<"),
        (" ".join(sl_parts), sl_slot_w, ">"),
    ]
    return slots

def _track_row_slots(title: str, track_number: str, track_count: int):
    """Build track row slots: label (7) + title (flex) + track num (dynamic).

    Track number is only displayed when BOTH track_number and track_count
    are available (format: "X / Y"). Otherwise, only the title is shown.
    """
    lw, gap = 7, 1

    # Normalize track_count to int for comparison
    try:
        track_count_int = int(track_count) if track_count else 0
    except (ValueError, TypeError):
        track_count_int = 0

    # Only show track number when both track number AND count are available
    show_track_num = bool(track_number) and track_count_int > 0

    if show_track_num:
        tn_text = f"{track_number} / {track_count_int}"
        tn_slot_w = len(tn_text)
        # Title width: inner - label - gap - title - gap - track_num
        tw = Config.INNER_W - lw - gap - gap - tn_slot_w
    else:
        tn_text = ""
        tn_slot_w = 0
        # Title width: inner - label - gap - title (no trailing gap)
        tw = Config.INNER_W - lw - gap

    # Truncate title if needed
    title_text = truncate(title, tw) if tw > 0 else ""

    label_colored = colorize(f"{'Track:':>{lw}}", Theme.DIM)

    slots = [
        (label_colored, lw, ">"),
        (title_text, tw, "<"),
    ]
    if show_track_num:
        tn_colored = colorize(f"{tn_text:>{tn_slot_w}}", Theme.DIM)
        slots.append((tn_colored, tn_slot_w, ">"))

    return slots


def album_row():
    global s
    return _info_row("Album:", s.state.album)


def track_row():
    """Track row: label + title + track number info."""
    global s
    # Build track row with optional track number display
    slots = _track_row_slots(
        s.state.title,
        s.state.trackNumber,
        s.state.trackCount,
    )
    return row(*slots)


def artist_row():
    """Artist row: label + artist name + shuffle/loop indicators."""
    global s
    slots = _artist_row_slots(
        s.state.artist,
        s.state.shuffle,
        s.state.loop,
    )
    return row(*slots)


def progress_row():
    """Progress row: time + bar + time."""
    global s
    start = format_time(s.state.position)  # elapsed time: MM:SS
    end = format_time(s.state.length)  # total time: shows hours if needed
    # Save time widths for volume row alignment
    s.state._start_time_w = len(start)
    s.state._end_time_w = len(end)
    bar_w = (
        Config.INNER_W - s.state._start_time_w - 1 - 1 - s.state._end_time_w
    )  # inner - start - gap - gap - end
    bar = progress_bar(s.state.position, s.state.length, bar_w)
    return row(
        (start, s.state._start_time_w, "<"),
        (bar, bar_w, "^"),
        (end, s.state._end_time_w, ">"),
    )


def _volume_icon(vol: int) -> str:
    """Get icon name for volume level (vol is 0-100)."""
    for key, name in VOL_ICONS.items():
        if isinstance(key, tuple):
            if key[0] <= vol <= key[1]:
                return name
        elif key == vol:
            return name
    return "vol-high"


def toolbar_row():
    """Toolbar with controls."""
    global s

    # Build each tool
    seek = f"{colorize(icon('seek'), Theme.KEY_HINT)} seek"  # 7
    vol = f"{colorize(icon('vol-change'), Theme.KEY_HINT)} volume"  # 9
    mute = f"{colorize('m', Theme.KEY_HINT)}ute"  # 4

    if s.state.status == "Playing":
        play_pause = f"{colorize(icon('toggle-play'), Theme.KEY_HINT)} pause"  # 7
    else:
        play_pause = f"{colorize(icon('toggle-play'), Theme.KEY_HINT)} play "

    prev = f"{colorize('p', Theme.KEY_HINT)}rev"  # 4
    next_ = f"{colorize('n', Theme.KEY_HINT)}ext"  # 4
    close = f"{colorize('esc/q', Theme.KEY_HINT)} close"  # 11

    # Combine all tools with 2-space separator
    tools = "  ".join([seek, vol, mute, play_pause, prev, next_, close])

    gaps_w = 6 * 2
    tool_w = 7 + 9 + 4 + 7 + 4 + 4 + 11 + gaps_w
    pad_w = int((Config.INNER_W - tool_w) / 2)
    pad = " " * pad_w

    return row((f"{pad}{tools:^{tool_w}}{pad}", Config.INNER_W, "^"))


def volume_row():
    """Volume row: icon + bar + percentage."""
    global s
    vol_pct = s.state.volume  # already int 0-100
    pct_text = f"{vol_pct}%"
    start_w = s.state._start_time_w or 0
    end_w = s.state._end_time_w or 0
    vol_icon = f" {icon(_volume_icon(vol_pct))} "
    bar_w = Config.INNER_W - start_w - 1 - 1 - end_w
    bar = volume_bar(vol_pct, max(0, bar_w))
    icon_w = max(start_w - 1, 0)
    return row(
        (pad_visible(vol_icon, icon_w, "^"), icon_w, "<"),
        (bar, max(0, bar_w), "^"),
        (pct_text, end_w, ">"),
    )


def update_state_from_metadata(data: dict):
    """Update state from parsed metadata dict."""
    global s

    # Debounce: skip if update came too soon after our optimistic update
    if time.time() - s.last_command_time < COMMAND_DEBOUNCE:
        return
    changed = False
    for key, value in data.items():
        if key == "player":
            continue  # preserve full player identifier from s.current_player
        if getattr(s.state, key, None) != value:
            setattr(s.state, key, value)
            changed = True
    if changed:
        s.state.dirty = True


# ─────────────────────────────────────────────────────────────────────────────
# UI Rendering
# ─────────────────────────────────────────────────────────────────────────────


def clear_screen():
    global s
    sys.stdout.write("\033[2J\033[H")
    if Theme.BG:
        sys.stdout.write(f"\033[48;2;{Theme.BG}m")
    sys.stdout.flush()
    s.state.dirty = False


def move_cursor(row: int, col: int):
    sys.stdout.write(f"\033[{row};{col}H")


ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def pad_visible(text: str, width: int, align: str = "<") -> str:
    """Pad text to visible width, accounting for wide characters (CJK, emoji)."""
    vw = visible_width(text)
    padding = max(0, width - vw)
    if align == "<":
        return text + " " * padding
    elif align == ">":
        return " " * padding + text
    elif align == "^":
        left = padding // 2
        right = padding - left
        return " " * left + text + " " * right
    return text + " " * padding


def row(*slots) -> str:
    """Build a content row from slots.

    Each slot is (content, slot_width, alignment). Content will be padded
    to slot_width using visible character width (accounts for CJK/emoji).
    """
    valid_slots = [s for s in slots if s is not None]

    if not valid_slots:
        return "│ │"

    # Build content with visible-width padding
    parts = []
    for content, width, align in valid_slots:
        parts.append(pad_visible(content, width, align))
    content_str = " ".join(parts)

    return f"{Theme.BORDER}│{Theme.RESET} {content_str} {Theme.BORDER}│{Theme.RESET}"


def visible_width(text: str) -> int:
    """Calculate display width of text, accounting for wide chars (CJK, emoji).
    
    Variation selectors (U+FE00-U+FE0F) are treated as zero width since they
    don't take up display space.
    """
    plain = ANSI_PATTERN.sub("", text)
    width = 0
    prev_was_combining = False
    for char in plain:
        cp = ord(char)
        # Variation selectors (U+FE00-U+FE0F) have zero width
        if 0xFE00 <= cp <= 0xFE0F:
            continue
        w = unicodedata.east_asian_width(char)
        width += 2 if w in ("F", "W") else 1  # Full-width or Wide = 2 columns
    return width


def truncate(text: str, width: int) -> str:
    """Truncate text to visible width, add ellipsis if needed."""
    text = text.replace("\n", " ").strip()
    if visible_width(text) <= width:
        return text
    # Build result keeping ANSI codes, truncating visible chars
    result = ""
    visible = 0
    i = 0
    while visible < width - 1 and i < len(text):
        if text[i] == "\x1b":
            # Copy entire ANSI sequence
            end = text.find("m", i)
            if end > i:
                result += text[i : end + 1]
                i = end + 1
            else:
                i += 1
        else:
            char = text[i]
            w = unicodedata.east_asian_width(char)
            char_width = 2 if w in ("F", "W") else 1
            if visible + char_width > width - 1:
                break
            result += char
            visible += char_width
            i += 1
    return result + "…"


def format_time(seconds: float) -> str:
    if seconds <= 0:
        return "0:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    if minutes > 0:
        return f"{minutes}:{secs:02d}"
    return f"0:{secs:02d}"


def progress_bar(current: float, total: float, total_width: int) -> str:
    if total <= 0:
        return "─" * total_width
    # Clamp current to total to prevent overflow
    clamped = min(current, total)
    # Reserve 1 char for indicator, so filled_w max is total_width - 1
    filled_w = min(int((clamped / total) * (total_width - 1)), total_width - 1)
    empty_w = total_width - filled_w - 1
    return (
        Theme.PROGRESS_FILL
        + "━" * filled_w
        + "\u25cf"
        + Theme.PROGRESS_EMPTY
        + "━" * empty_w
        + Theme.RESET
    )


def _color_rgb(color_seq: str) -> str:
    """Extract RGB values from a color escape sequence like '\033[38;2;R;G;Bm'."""
    # Format: \033[38;2;R;G;Bm
    nums = color_seq[2:-1].split(";")  # strip \033[ and m, split by ;
    return f"{nums[2]};{nums[3]};{nums[4]}"  # R;G;B


def volume_bar(volume: int, width: int) -> str:
    """Build VU-meter style volume bar with dithered color gradient.
    
    Zones: green (0-50%), yellow (50-80%), red (80-100%)
    Transitions use half-block characters (▒▓█) with FG/BG color mixing.
    Empty section uses dimmed color for both FG and BG.
    """
    if volume == 0:
        # Muted: dimmed FG and BG
        return f"\033[38;2;{_color_rgb(Theme.VOL_EMPTY)}m\033[48;2;{_color_rgb(Theme.VOL_EMPTY)}m{'░' * width}{Theme.RESET}"
    
    filled = min(int(volume * width // 100), width)
    
    # Zone boundaries
    green_zone_end = int(width * 0.50)   # exclusive
    yellow_zone_end = int(width * 0.80)  # exclusive
    
    empty_rgb = _color_rgb(Theme.VOL_EMPTY)
    
    result = []
    for i in range(width):
        if i < filled:
            # Determine zone and whether we're in transition
            if i < green_zone_end:
                # Green zone
                if filled > green_zone_end and i == green_zone_end - 1:
                    # At boundary, transitioning to yellow
                    block = "▒"
                    fg_rgb = _color_rgb(Theme.VOL_MED)
                    bg_rgb = _color_rgb(Theme.VOL_LOW)
                    result.append(f"\033[38;2;{fg_rgb}m\033[48;2;{bg_rgb}m{block}")
                else:
                    result.append(f"{Theme.VOL_LOW}█")
            elif i < yellow_zone_end:
                # Yellow zone
                if filled > yellow_zone_end and i == yellow_zone_end - 1:
                    # At boundary, transitioning to red
                    block = "▒"
                    fg_rgb = _color_rgb(Theme.VOL_HIGH)
                    bg_rgb = _color_rgb(Theme.VOL_MED)
                    result.append(f"\033[38;2;{fg_rgb}m\033[48;2;{bg_rgb}m{block}")
                else:
                    result.append(f"{Theme.VOL_MED}█")
            else:
                # Red zone
                result.append(f"{Theme.VOL_HIGH}█")
        else:
            # Empty: reset all, then set dimmed FG and BG using VOL_EMPTY theme color
            empty_rgb = _color_rgb(Theme.VOL_EMPTY)
            result.append(f"\033[0m\033[38;2;{empty_rgb}m\033[48;2;{empty_rgb}m░")
    
    return "".join(result) + Theme.RESET


def run_playerctl_async(*args) -> None:
    """Fire-and-forget playerctl command. Does not block the main loop."""

    def _exec():
        _playerctl_subprocess(list(args), timeout=0.3, capture=False)

    _playerctl_pool.submit(_exec)


def handle_key(key: str, seq: str = "") -> None:
    global s, shutdown_requested

    now = time.time()
    if key != "q" and key != "Q" and key != "\x1b" and now - s.last_command_time < COMMAND_COOLDOWN:
        return  # Ignore rapid repeats
    # Quit bypasses cooldown
    if key in {"q", "Q"} or (key == "\x1b" and not seq):
        cleanup()
        shutdown_requested = True
        return

    if now - s.last_command_time < COMMAND_COOLDOWN:
        return  # Ignore rapid repeats
    s.last_command_time = now

    if key == "\x1b":
        if seq == "[A":
            # Volume up: volume is int 0-100
            vol = min(100, s.state.volume + 5)
            # Format volume as float for playerctl
            vol_arg = f"{vol / 100:.2f}"
            run_playerctl_async("volume", vol_arg)
            s.state.volume = vol
        elif seq == "[B":
            # Volume down: volume is int 0-100
            vol = max(0, s.state.volume - 5)
            # Format volume as float for playerctl
            vol_arg = f"{vol / 100:.2f}"
            run_playerctl_async("volume", vol_arg)
            s.state.volume = vol
        elif seq == "[C":
            # Seek forward: optimistic update
            s.state.position = min(s.state.length, s.state.position + Config.SEEK_SECONDS)
            run_playerctl_async("position", f"{Config.SEEK_SECONDS}+")
        elif seq == "[D":
            # Seek backward: optimistic update
            s.state.position = max(0, s.state.position - Config.SEEK_SECONDS)
            run_playerctl_async("position", f"{Config.SEEK_SECONDS}-")
        else:
            return
        s.state.dirty = True
        return

    if key == " ":
        # Optimistic update
        if s.state.status == "Playing":
            s.state.status = "Paused"
        else:
            s.state.status = "Playing"
        run_playerctl_async("play-pause")
    elif key in {"n", "N"}:
        run_playerctl_async("next")
    elif key in {"p", "P"}:
        run_playerctl_async("previous")
    elif key in {"s", "S"}:
        # Optimistic update: toggle shuffle
        s.state.shuffle = "false" if s.state.shuffle == "true" else "true"
        run_playerctl_async("shuffle", "Toggle")
    elif key in {"l", "L"}:
        # Optimistic update: cycle loop
        if s.state.loop == "None":
            s.state.loop = "Track"
            run_playerctl_async("loop", "Track")
        elif s.state.loop == "Track":
            s.state.loop = "Playlist"
            run_playerctl_async("loop", "Playlist")
        else:
            s.state.loop = "None"
            run_playerctl_async("loop", "None")
    elif key in {"m", "M"}:
        # Mute/unmute (volume is int 0-100)
        if s.state.volume > 0:
            # Mute: store current volume for restore
            s.state.pre_mute_volume = s.state.volume
            run_playerctl_async("volume", "0.0")
            s.state.volume = 0
        else:
            # Unmute: restore to pre-mute volume (or 50% if first mute)
            restore_vol = s.state.pre_mute_volume if s.state.pre_mute_volume > 0 else 50
            run_playerctl_async("volume", f"{restore_vol / 100:.2f}")
            s.state.volume = restore_vol
    else:
        return

    s.state.dirty = True


# ─────────────────────────────────────────────────────────────────────────────
# Main event loop
# ─────────────────────────────────────────────────────────────────────────────


def enable_raw_mode(fd: int):
    """Enable raw mode on fd. Returns old_settings or None if not a tty."""
    if not os.isatty(fd):
        return None
    try:
        import termios

        old_settings = termios.tcgetattr(fd)
        new_settings = termios.tcgetattr(fd)
        new_settings[3] &= ~(termios.ICANON | termios.ECHO)
        new_settings[6][termios.VMIN] = 0
        new_settings[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
        return old_settings
    except ImportError:
        return None


def disable_raw_mode(fd: int, old_settings) -> None:
    """Restore terminal settings from enable_raw_mode."""
    if old_settings is None:
        return
    try:
        import termios

        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except ImportError:
        pass


def read_key(fd: int):
    """Read a keypress from fd. Returns (key, seq) or None.

    seq is populated for escape sequences (e.g., '[A' for arrow up).
    Returns None if no input available.
    """
    r, _, _ = select.select([fd], [], [], 0.0)
    if fd not in r:
        return None
    try:
        c = os.read(fd, 1)
        if not c:
            return None
    except OSError:
        return None

    ch = c.decode("utf-8", errors="replace")
    if ch != "\x1b":
        return (ch, "")

    # Escape sequence
    r, _, _ = select.select([fd], [], [], 0.02)
    if fd not in r:
        return (ch, "")
    try:
        c2 = os.read(fd, 1)
        if not c2:
            return (ch, "")
    except OSError:
        return (ch, "")

    ch2 = c2.decode("utf-8", errors="replace")
    if ch2 != "[":
        return (ch, ch2)

    r, _, _ = select.select([fd], [], [], 0.1)
    if fd not in r:
        return (ch, ch2)
    try:
        c3 = os.read(fd, 1)
        if not c3:
            return (ch, ch2)
    except OSError:
        return (ch, ch2)

    ch3 = c3.decode("utf-8", errors="replace")
    return (ch, ch2 + ch3)


def read_metadata_from_follower(raw: str) -> None:
    """Parse and apply metadata from a raw follower data chunk.

    Handles partial blocks (playerctl only sends non-empty fields).
    """
    parts = raw.split("\n@")
    if not parts:
        return
    # parts[0] is empty (before leading \n) or '@0@val' (without leading \n)
    # Normalize: prepend '' so parsing is uniform
    if parts[0] != "":
        parts = [""] + parts
    # Process all fields at once (may be < 39)
    block = "@" + "\n@".join(parts[1:])
    parsed = parse_metadata(block)
    if parsed:
        update_state_from_metadata(parsed)


def main():
    global s

    check_playerctl()  # Exit early if playerctl not available
    setup_signals()
    detect_and_apply_terminal_width()  # Clamp UI_WIDTH to terminal width (max 72)

    # Hide cursor
    sys.stdout.write("\033[?25l")
    # Set background color if configured
    if Theme.BG:
        sys.stdout.write(f"\033[48;2;{Theme.BG}m")
    sys.stdout.flush()

    try:
        s.available_players = get_available_players()
        s.current_player = get_best_player(s.available_players) or ""
        if s.current_player:
            s.current_player_idx = s.available_players.index(s.current_player)
            s.state.player = s.current_player
            # Query shuffle and loop state (not in metadata follower)
            # Normalize shuffle: "Off"/"On" (Spotify) or "true"/"false" (MPRIS)
            shuffle_val = run_playerctl("shuffle").strip().lower()
            s.state.shuffle = "true" if shuffle_val in ("on", "true") else "false"
            # Loop: "None", "Track", "Playlist" (capitalized in MPRIS)
            s.state.loop = run_playerctl("loop").strip() or "None"
            s.state.dirty = True
        else:
            s.current_player_idx = -1
            s.state.status = "No MPRIS player"
            s.state.dirty = True

        s.meta_proc = start_metadata_follower() if s.current_player else None

        clear_screen()
        render_ui()  # Render initial state before entering the loop

        stdin_fd = None
        old_settings = None
        if os.isatty(sys.stdin.fileno()):
            stdin_fd = sys.stdin.fileno()
            old_settings = enable_raw_mode(stdin_fd)

        def build_select_list():
            fds = []
            if s.meta_proc and s.meta_proc.stdout:
                fds.append(s.meta_proc.stdout)
            if stdin_fd is not None:
                fds.append(stdin_fd)
            return fds

        while not shutdown_requested:
            fds = build_select_list()
            if not fds:
                time.sleep(0.1)
                continue
            readable, _, _ = select.select(fds, [], [], 0.5)

            if s.meta_proc and s.meta_proc.stdout in readable:
                try:
                    data = os.read(s.meta_proc.stdout.fileno(), 4096)
                    if data:
                        decoded = data.decode("utf-8", errors="replace")
                        read_metadata_from_follower(decoded)
                except OSError:
                    pass

                # Check if process died
                if s.meta_proc.poll() is not None:
                    cleanup_proc(s.meta_proc)
                    s.meta_proc = start_metadata_follower() if s.current_player else None

            if stdin_fd is not None and stdin_fd in readable:
                result = read_key(stdin_fd)
                if result is None:
                    continue
                ch, seq = result
                if ch == "\t":
                    switch_player()
                else:
                    handle_key(ch, seq)

            if s.state.dirty:
                render_ui()

    finally:
        disable_raw_mode(stdin_fd, old_settings)
        sys.stdout.write("\033[?25h")
        sys.stdout.write("\033[49m")  # Reset background
        sys.stdout.write("\033[0m")  # Reset all attributes
        sys.stdout.flush()
        clear_screen()
        cleanup()


if __name__ == "__main__":
    main()
