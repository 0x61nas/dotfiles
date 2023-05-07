### Screenshots 
![](./Screenshots/zsh-neofetch-kitty-cmus-notify-v0.3.png)
![](./Screenshots/zsh-neofetch-kitty-cava-tty_clock-v0.3.png)
![](./Screenshots/zsh-kitty-v0.3.png)

### Ref
* If u use a laptop like me and only use [yo-dwm](https://github.com/anas-elgarhy/yo-dwm) or any other standalone WM u may notch that the touchpad doesn't work as you expect (like u can't perform the mouse buttons clicks with it), in this case, you need to configure the touchpad driver(and maybe download the driver itself). In most cases [libinput](https://wiki.archlinux.org/title/Libinput) is more than enough and it's installed by default with Xorg-server and Wayland, but in my case, I go with [synaptics](https://wiki.archlinux.org/title/Touchpad_Synaptics#Natural_scrolling) at least for now 'cause why not?, see [30-touchpad.conf](./etc/X11/xorg.conf.d/30-touchpad.conf)
* When u use ur laptop as a daily driver then u may be concerned about the battery life (especially when u using a gaming laptop) and if ur laptop is from Lenovo like me u maybe used to have control over the charger to select a specific percentage for the battery and when the battery reaches it the laptop will stop the charging and it'll run on the charger only without taking anything from the battery and u save your battery life by reducing the charging cycles and the all is happy :D, so u can use [tlp] tlp on arch wiki] for this job and u can see(or steal) my configure from [tlp.conf](./etc/tlp.conf) which is just the default one with enabling the threshold mode to stop charging at 60%

### Also available on
* [GitLab](https://gitlab.com/Anas-Elgarhy/dotfiles)
* [BitBucket](https://bitbucket.org/anas_elgarhy/dotfiles)
* [Codeberg](https://codeberg.org/anas-elgarhy/dotfiles)
* [Notabug](https://notabug.org/anas-elgarhy/dotfiles) not instant updated
* [disroot](https://git.disroot.org/anas-elgarhy/dotfiles)

[tlp on arch wiki]: https://wiki.archlinux.org/title/TLP
