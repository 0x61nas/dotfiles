## Screenshots 
![](./Screenshots/zsh-neofetch-kitty-cmus-notify-v0.3.png)
![](./Screenshots/zsh-neofetch-kitty-cava-tty_clock-v0.3.png)
![](./Screenshots/zsh-kitty-v0.3.png)

## Ref
### Laptop stuff
* If u use a laptop like me and only use [yo-dwm][yo-dwm on github] or any other standalone WM u may notch that the touchpad doesn't work as you expect (like u can't perform the mouse button clicks with it), in this case, you need to configure the touchpad driver(and maybe download the driver itself). In most cases [libinput][libinput on arch wiki] is more than enough and it's installed by default with Xorg-server and Wayland, and this is what I'll go with. see [30-touchpad.conf](./etc/X11/xorg.conf.d/30-touchpad.conf), but you maybe want to use [synaptics][synaptics on arch wiki] instant if u want a specific feature that doesn't exist in libinput yet like the Circular scrolling
    > I notch that the disable touchpad while typing option doesn't work with me when I trayd synaptics idk why but it works just fine with libinput
* When u use ur laptop as a daily driver then u may be concerned about the battery life (especially when u using a gaming laptop) and if ur laptop is from Lenovo like me u maybe used to have control over the charger to select a specific percentage for the battery and when the battery reaches it the laptop will stop the charging and it'll run on the charger only without taking anything from the battery and u save your battery life by reducing the charging cycles and the all is happy :D, so u can use [tlp][tlp on arch wiki] for this job and u can see(or steal) my configure from [tlp.conf](./etc/tlp.conf) which is just the default one with enabling the threshold mode to stop charging at 60%

### other
#### Browser
* If u want to put the tabs on the bottom of the window on Firefox then u have to move the [userChrome.css](./.mozilla/firefox/chrome/userChrome.css) file into ur Firefox user directory(u can find it in `~/.mozilla/firefox/`) in the `chrome` dir or create it if doesn't exist, and then u have to enable the `legacy user profile customizations stylesheets feature from [about:config](about:config)

## Also available on
* [GitLab](https://gitlab.com/Anas-Elgarhy/dotfiles)
* [BitBucket](https://bitbucket.org/anas_elgarhy/dotfiles)
* [Codeberg](https://codeberg.org/anas-elgarhy/dotfiles)
* [Notabug](https://notabug.org/anas-elgarhy/dotfiles) not instant updated
* [disroot](https://git.disroot.org/anas-elgarhy/dotfiles)

[yo-dwm on github]: https://github.com/anas-elgarhy/yo-dwm
[libinput on arch wiki]: https://wiki.archlinux.org/title/Libinput
[synaptics on arch wiki]: https://wiki.archlinux.org/title/Touchpad_Synaptics
[tlp on arch wiki]: https://wiki.archlinux.org/title/TLP
