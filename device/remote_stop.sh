#!/bin/sh
rm -rf /tmp/*
for proc in ps5-jailbreak host.py socat dnsmasq; do
    kill $(ps | awk -v p=$proc '$0 ~ p && !/awk/ {print $1}') 2>/dev/null
done
sleep 1
rm -rf /userdata/umtx2 /userdata/ps5-linux-loader.elf /root/umtx2 /root/ps5-linux-loader.elf /userdata/socat /root/socat \
    /usr/local/bin/ps5-jailbreak.sh /etc/init.d/S99ps5jailbreak /etc/dnsmasq.conf /var/lib/misc/dnsmasq.leases \
    /tmp/remote_setup.sh /tmp/remote_stop.sh /root/remote_setup.sh /userdata/remote_setup.sh \
    /etc/init.d/S98hidsetup \
    /usr/local/bin/bt_wake.py /usr/local/bin/hid_navigate.py /usr/local/bin/nav_sequence.py \
    /usr/local/bin/ps5_os_detect.py /usr/local/bin/usb_backend_fix.py /usr/local/bin/bt_config.json \
    /usr/local/bin/__pycache__ \
    /lib/modules/$(uname -r)/kernel/drivers/usb/gadget/function/usb_f_hid.ko \
    /usr/lib/libusb-1.0.so /usr/lib/libusb-1.0.so.0 /usr/lib/libusb-1.0.so.0.3.0
sed -i '/^usb_f_hid$/d' /etc/modules 2>/dev/null
echo "[*] Cleanup complete"