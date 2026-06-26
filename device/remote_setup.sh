#!/bin/sh

# PS5 ethernet interface passed by setup_luckfox.py; default to eth0
PS5_ETH="${1:-eth0}"

MODEL=$(cat /proc/device-tree/model 2>/dev/null)
case "$MODEL" in
    *"Lyra"*)
        BASE="/root"
        ;;
    *)
        BASE="/userdata"
        ;;
esac

echo "[*] Detected device: $MODEL"
echo "[*] Using base path: $BASE"
echo "[*] PS5 ethernet interface: $PS5_ETH"

mkdir -p /usr/local/bin
mkdir -p $BASE/umtx2
chmod +x $BASE/socat

cat > /etc/dnsmasq.conf << DNSEOF
interface=$PS5_ETH
bind-interfaces
dhcp-range=192.168.100.10,192.168.100.50,12h
dhcp-option=3,192.168.100.1
dhcp-option=6,192.168.100.1
address=/manuals.playstation.net/192.168.100.1
DNSEOF

mkdir -p /var/lib/misc
touch /var/lib/misc/dnsmasq.leases

# --- Optional: HID gadget kernel module + init script (Lyra Pi only) ---
# This image's BusyBox has no `depmod`, so `modprobe usb_f_hid` can never find a
# manually-dropped-in .ko (no modules.dep entry, and no way to regenerate one). We
# load it directly with `insmod <path>` instead, both now and on every boot from
# S98hidsetup, rather than relying on modprobe/`/etc/modules`.
if [ -f "$BASE/usb_f_hid.ko" ]; then
    echo "[*] Installing HID gadget kernel module..."
    KMOD_DIR="/lib/modules/$(uname -r)/kernel/drivers/usb/gadget/function"
    mkdir -p "$KMOD_DIR"
    cp "$BASE/usb_f_hid.ko" "$KMOD_DIR/usb_f_hid.ko"
    rm -f "$BASE/usb_f_hid.ko"
    insmod "$KMOD_DIR/usb_f_hid.ko" 2>/dev/null || true

    cat > /etc/init.d/S98hidsetup << 'HIDEOF'
#!/bin/sh

case "$1" in
  start)
    insmod /lib/modules/$(uname -r)/kernel/drivers/usb/gadget/function/usb_f_hid.ko 2>/dev/null
    echo "Waiting for USB gadget to be ready..."
    for i in $(seq 1 30); do
        if [ -s /sys/kernel/config/usb_gadget/rockchip/UDC ]; then
            break
        fi
        sleep 0.5
    done
    sleep 2

    echo "Setting up HID gadget..."
    cd /sys/kernel/config/usb_gadget/rockchip/functions
    mkdir -p hid.0
    cd hid.0
    echo 1 > protocol
    echo 1 > subclass
    echo 8 > report_length
    echo -ne "\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x03\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x03\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0" > report_desc

    echo "" > /sys/kernel/config/usb_gadget/rockchip/UDC
    ln -sf /sys/kernel/config/usb_gadget/rockchip/functions/hid.0 /sys/kernel/config/usb_gadget/rockchip/configs/b.1/f-hid.0
    sleep 1
    echo "ff740000.usb" > /sys/kernel/config/usb_gadget/rockchip/UDC

    echo "HID gadget setup complete." >> /var/log/hidsetup.log
    ls /dev/hidg* >> /var/log/hidsetup.log 2>&1
    ;;
  stop)
    echo "Stopping HID gadget..."
    ;;
  restart)
    $0 stop
    $0 start
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
    ;;
esac

exit 0
HIDEOF
    chmod +x /etc/init.d/S98hidsetup
fi

# --- Optional: libusb (Lyra Pi only) ---
# Needed by pyusb for pywakepsx-on-bt's extract_psx_bt_macs() (reads the DualSense's
# feature report over USB to detect controller/console BT MAC addresses). Built from
# the Luckfox Lyra Buildroot SDK -- this image ships no libusb of its own.
if [ -f /tmp/libusb-1.0.so.0.3.0 ]; then
    echo "[*] Installing libusb..."
    cp /tmp/libusb-1.0.so.0.3.0 /usr/lib/libusb-1.0.so.0.3.0
    ln -sf libusb-1.0.so.0.3.0 /usr/lib/libusb-1.0.so.0
    ln -sf libusb-1.0.so.0.3.0 /usr/lib/libusb-1.0.so
    rm -f /tmp/libusb-1.0.so.0.3.0
fi

# --- Optional: pywakepsx-on-bt for Bluetooth wake (Lyra Pi only) ---
# Installed from wheels staged to /tmp/wheels by setup_luckfox.py (downloaded on the
# PC ahead of time) so the device never needs its own internet/DNS access or a correct
# clock to do this -- both were unreliable on this board and caused setup to hang/fail.
if [ -f /usr/local/bin/bt_wake.py ]; then
    chmod +x /usr/local/bin/bt_wake.py /usr/local/bin/hid_navigate.py /usr/local/bin/ps5_os_detect.py 2>/dev/null || true

    python3 -m ensurepip >/dev/null 2>&1 || true
    if ! python3 -c "import pywakepsx_on_bt" 2>/dev/null; then
        if [ -d /tmp/wheels ]; then
            echo "[*] Installing pywakepsx-on-bt from local wheels..."
            pip3 install --quiet --no-index --find-links /tmp/wheels pywakepsx-on-bt || echo "[!] pywakepsx-on-bt install from local wheels failed"
            rm -rf /tmp/wheels
        else
            echo "[!] No local wheels staged at /tmp/wheels -- skipping pywakepsx-on-bt install"
        fi
    fi

    # The Lyra Pi is bus-powered from the PS5's own USB port (needed for HID gadget
    # mode), and the PS5 briefly cuts USB power (~2s) on both entering AND waking from
    # rest mode, even with "Supply Power to USB Ports" enabled -- this reboots the Pi
    # before the main loop's in-band wake step can ever run. Fix: fire the wake
    # unconditionally on every boot instead of waiting for the loop to observe rest
    # mode. Sending the magic packet while the PS5 is already awake/in Linux is
    # harmless -- it's simply ignored.
    #
    # Separately, hci1 (the USB BT dongle) often comes up DOWN right after boot --
    # bluetoothd doesn't register it via MGMT and a single `hciconfig hci1 up` can
    # silently fail ("Network is down" when bt_wake.py opens the raw HCI socket).
    # Retrying `hciconfig hci1 up` with verification (not just firing it once) is
    # what actually makes this reliable.
    cat > /etc/init.d/S97btwake << 'BTEOF'
#!/bin/sh
case "$1" in
    start)
        echo "Starting BT wake-on-boot..."
        (
            for i in $(seq 1 20); do
                if hciconfig hci1 >/dev/null 2>&1; then
                    break
                fi
                sleep 1
            done

            for i in $(seq 1 15); do
                hciconfig hci1 up 2>/dev/null
                sleep 2
                if hciconfig hci1 | grep -q "UP RUNNING"; then
                    echo "hci1 is up after attempt $i"
                    break
                fi
            done

            cd /usr/local/bin && python3 bt_wake.py
        ) > /tmp/bt_wake_boot.log 2>&1 &
        ;;
    stop)
        ;;
    restart)
        "$0" stop
        "$0" start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
exit 0
BTEOF
    chmod +x /etc/init.d/S97btwake
fi

# --- Main loop script ---
cat > /usr/local/bin/ps5-jailbreak.sh << EOF
#!/bin/sh
ELF="$BASE/ps5-linux-loader.elf"
LEASES="/var/lib/misc/dnsmasq.leases"

ip addr add 192.168.100.1/24 dev $PS5_ETH 2>/dev/null || true
ip link set $PS5_ETH up

dnsmasq -C /etc/dnsmasq.conf

(cd $BASE/umtx2 && python3 host.py) > /tmp/host.log 2>&1 &

echo "[*] Exploit server running. Waiting for PS5..."

while true; do
    while [ -z "\$(awk 'NF{print \$3}' "\$LEASES" | head -1)" ]; do
        sleep 2
    done

    PS5_IP=\$(awk 'NF{print \$3}' "\$LEASES" | head -1)
    echo "[*] PS5 detected at \$PS5_IP"

    if [ -f /usr/local/bin/ps5_os_detect.py ] && [ -e /dev/hidg0 ]; then
        echo "[*] Waiting for PS5 OS ports (up to 60s)..."
        PS5_OS_DETECTED=0
        for i in \$(seq 1 30); do
            if python3 -c "import sys; sys.path.insert(0, '/usr/local/bin'); from ps5_os_detect import is_ps5_os; sys.exit(0 if is_ps5_os('\$PS5_IP') else 1)" 2>/dev/null; then
                PS5_OS_DETECTED=1
                break
            fi
            sleep 2
        done
        if [ "\$PS5_OS_DETECTED" = "1" ]; then
            echo "[*] PS5 OS detected, running HID navigation..."
            python3 /usr/local/bin/hid_navigate.py
        else
            echo "[*] Linux already running on PS5, skipping navigation."
        fi
    fi

    echo "[*] Waiting for jailbreak trigger..."
    > /tmp/host.log

    while true; do
        if grep -q "elfldr-ps5.elf" /tmp/host.log 2>/dev/null; then
            echo "[*] ELF loader fetched, waiting 3 seconds..."
            sleep 3
            echo "[*] Sending ps5-linux-loader.elf..."
            $BASE/socat -t 99999999 - TCP:\${PS5_IP}:9021 < "\$ELF" > /tmp/socat.log 2>&1 &
            SOCAT_PID=\$!
            while true; do
                if grep -q "Going to rest mode" /tmp/socat.log 2>/dev/null; then
                    echo "[*] Done. PS5 going to rest mode."
                    kill \$SOCAT_PID 2>/dev/null
                    break
                fi
                sleep 1
            done
            break
        fi
        sleep 1
    done

    echo "[*] Standing by for next run..."
    > /tmp/host.log
    > /tmp/socat.log
    sleep 5
done
EOF
chmod +x /usr/local/bin/ps5-jailbreak.sh

cat > /etc/init.d/S99ps5jailbreak << 'EOF'
#!/bin/sh
case "$1" in
    start)
        echo "Starting PS5 jailbreak server..."
        /usr/local/bin/ps5-jailbreak.sh > /tmp/ps5-jailbreak.log 2>&1 &
        ;;
    stop)
        echo "Stopping PS5 jailbreak server..."
        for proc in ps5-jailbreak host.py dnsmasq; do
            kill $(ps | awk -v p=$proc '$0 ~ p && !/awk/ {print $1}') 2>/dev/null
        done
        ;;
    restart)
        "$0" stop
        sleep 1
        "$0" start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
exit 0
EOF
chmod +x /etc/init.d/S99ps5jailbreak

echo "[*] Setup complete. Rebooting..."
reboot
