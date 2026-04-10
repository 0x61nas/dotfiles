
root_uuid=$(lsblk -o NAME,UUID | grep nvme0n1p2 | awk '{print $NF}')

cat <<EOF > /boot/loader/entries/arch.conf
title   Arch Linux
linux   /vmlinuz-linux
initrd /intel-ucode.img
initrd  /initramfs-linux.img
options splash root=UUID=$root_uuid rw
EOF

cat <<EOF > /boot/loader/entries/arch.conf
title   Arch Linux
linux   /vmlinuz-linux
initrd /intel-ucode.img
initrd  /initramfs-linux.img
options splash root=UUID=$root_uuid rw
EOF
