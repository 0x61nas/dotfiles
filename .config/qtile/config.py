from libqtile import hook, qtile

from libqtile import bar, layout, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen, KeyChord
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

mod = "mod4"
terminal = guess_terminal()

# def _change_bar_color(color: str):
#     qtile.current_screen.bottom.background = color
#     qtile.current_screen.bottom.draw()
#
#
# def _clear_bar_color():
#     _change_bar_color("#00000000")
#
#
# def _restore_bar_color():
#     _change_bar_color(bar_color)
#
#
# @hook.subscribe.setgroup
# @hook.subscribe.client_killed
# def on_setgroup_and_clinet_killed(c=None):
#     if hasattr(qtile, "current_screen"):
#         windows = len(qtile.current_group.windows)
#         if (windows == 0) or (windows == 1 and c):
#             _clear_bar_color()
#         else:
#             _restore_bar_color()
#
#
# @hook.subscribe.client_new
# def on_client_new(c):
#     if hasattr(qtile, "current_screen"):
#         if len(qtile.current_group.windows) > 0 or c:
#             _restore_bar_color()
#         else:
#             _clear_bar_color()

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    Key([mod], "b", lazy.hide_show_bar(), desc="Toggle bar"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod, "shift"], "space", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "Tab", lazy.screen.toggle_group(), desc="Move to the last visited group"),
    # Kill focused window
    KeyChord([mod], "q", [
        Key([], "q", lazy.window.kill(), desc="Kill focused window")
        ]),
    Key(["mod4"], "e", lazy.spawn("rofi -show emoji"), desc="Launch the emoji selector (rofi)"),
    Key([mod], "space", lazy.widget["keyboardlayout"].next_keyboard(), desc="Next keyboard layout."),
    Key([mod], "Print", lazy.spawn("spectacle"), desc="Launch screen shot tool (spectacle)"),

    Key([mod], "d", lazy.spawn("rofi -show drun"), desc="Run rofi luancher"),
    KeyChord([mod], "t", [
        Key([], "a", lazy.spawn("alacritty"), desc="Launch alacritty terminal"),
        Key([], "k", lazy.spawn("kitty"), desc="Launch kitty terminal")
        ]),

    ### Web browsers
    KeyChord([mod], "w", [
        Key([], "g", lazy.spawn("google-chrome-stable"), desc="Launch google-chrome-stable"),
        Key([], "t", lazy.spawn("tor-browser"), desc="Lanuch tor-browser"),
        Key([], "f", lazy.spawn("firfox"), desc="Lanuch firfox browser")
        ]),

    ### File browsers
    KeyChord([mod], "f", [
        Key([], "g", lazy.spawn("pcmanfm"), desc="Launch the GUI file manger (pcmanfm)"),
        Key([], "t", lazy.spawn(terminal + " -e ranger"), desc="Launch the tui file manger(ranger) in the default terminal"),
        Key([], "r", lazy.spawn("rofi -show filebrowser"), desc="Lanuch the rofi file browser")
        ]),

    ### Multi media apps
    KeyChord([mod], "m", [
        Key([], "c", lazy.spawn(terminal + " -e cmus"), desc="Launch cmus player"),
        Key([], "v", lazy.spawn("vlc"), desc="Launch vlc")
        ]),

    ### Start the caht/email/\* apps
    KeyChord([mod] , "c", [
        Key([], "d", lazy.spawn("discord"), desc="Launch discord"),
        Key([], "o", lazy.spawn("obsidian"), desc="Launch obsidian")
        ]),

    ### Start the dev apps
    KeyChord([mod], "a", [
        Key([], "j", lazy.spawn("jetbrains-toolbox"), desc="Lunch jetbrains-toolbox"),
        Key([], "n", lazy.spawn(terminal + " -e nvim"), desc="Lunch neovim in the default terminal"),
        Key([], "v", lazy.spawn(terminal + " -e vim"), desc="Lunch vim in the default terminal"),
        Key([], "e", lazy.spawn("emacs"), desc="Lunch emacs")
        ]),
    
    ### Start personalize apps
    KeyChord([mod], "p", [
        Key([], "b", lazy.spawn("nitrogen"), desc="Lunch the background manger (nitrogen)"),
        Key([], "n", lazy.spawn("nm-connection-editor"), desc="Lunch the network manager (nm-connection-editor)")
        ]),


    ### Controls keys
    # Screen
    Key([], "XF86MonBrightnessUp",   lazy.spawn("xbacklight -inc 5")),
    Key([], "XF86MonBrightnessDown", lazy.spawn("xbacklight -dec 5")),
    # Sound
    Key([], "XF86AudioRaiseVolume", lazy.spawn("pamixer --allow-boost -i 4")),
    Key([], "XF86AudioLowerVolume", lazy.spawn("pamixer --allow-boost -d 4")),
    Key([], "XF86AudioMute", lazy.spawn("pamixer -t"), desc="Toggle mute audio"),
    # Mic
    Key([], "XF86AudioMicMute", lazy.spawn("pactl set-source-mute @DEFAULT_SOURCE@ toggle")),
    # Players control
    Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause")),
    Key([], "XF86AudioStop", lazy.spawn("playerctl stop")),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next")),
    Key([], "XF86AudioPrev", lazy.spawn("playerctl previous")),

    Key([mod, "shift"], "x", lazy.spawn("betterlockscreen -l dim"), desc="Lock screen"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),

]

groups = [Group(i) for i in "123456789."]

for i in groups:
    keys.extend(
        [
            # mod1 + letter of group = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod1 + shift + letter of group = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod1 + shift + letter of group = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

layouts = [
    layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"], border_width=1),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    layout.MonadTall(),
    layout.MonadWide(),
    # layout.RatioTile(),
    layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        bottom=bar.Bar(
            [
                widget.GroupBox(),
                widget.CurrentLayout(),
                widget.WindowCount(text_format="[{num}]"),
                widget.Prompt(),
                widget.Spacer(),
                widget.WindowName(),
                widget.Spacer(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                widget.Systray(),
                widget.CPU(),
                widget.ThermalSensor(update_interval=2),
                widget.TextBox("🔊"),
                widget.Volume(emoji=False, volume_up_command="",
                    volume_down_command=""),
                widget.Battery(format="🔋{char} {percent:2.0%}"),
                widget.Backlight(backlight_name="nvidia_0", format="🌞{percent:2.0%}"),
                widget.Clock(format="🗓️%Y-%m-%d %a 🕑%I:%M:%S %p"),
                widget.KeyboardLayout(configured_keyboards=['us', 'ar']),
                widget.QuickExit(),
            ],
            24,
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
