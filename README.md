# luckma-ps5

## Zero config automated jailbreak host, linux loader, and linux reboot handler for linux-compatible PS5s utilizing Luckfox SBCs

# [Big Obvious Download Button Here](https://github.com/BringusStudios/luckma-ps5/releases)

Online shopping links listed here are affiliate links that generate me a small revenue when purchased from

## Supported Boards

| Board | Jailbreak & linux loader host | Auto PS5 Menu Navigation For Reboots | Auto Wake From Rest |
|-------|:-------------------:|:--------------:|:----------------:|
| [Luckfox Lyra Pi](https://www.luckfox.com/Mini-PC/Luckfox-Lyra-Pi) | ✅ | ✅ | ✅ |
| [Luckfox Lyra / Lyra Plus](https://www.luckfox.com/Mini-PC/Luckfox-Lyra) | ✅ | ❌ | ❌ |
| [Luckfox Pico Plus](https://www.luckfox.com/Luckfox-Pico/Luckfox-Pico-Plus) | ✅ | ❌ | ❌ |

### Lyra Pi (recommended)
The most feature-rich option. Once set up, it requires **zero interaction** on every boot cycle to boot/reboot linux:
1. PS5 reboots
2. Lyra Pi detects that it's connected to the PS5 OS via port scan
3. In the PS5 OS, HID keyboard emulation navigates to the User Guide automatically
4. Exploit loads
5. Linux loader ELF is delivered via socat automatically after exploit
6. PS5 enters rest mode
7. Lyra Pi sends an emulated dualsense wake packet to the PS5
8. Linux boots
9. Repeat 5ever

### Lyra / Lyra Plus & Pico Plus
These boards serve the exploit page and deliver the loader automatically, but **you still need to manually navigate to Settings → User's Guide** on the PS5 each time to trigger it upon boot/reboot.

## Compatibility

**A linux-compatible & umtx2 compatible PS5** (check [here](https://github.com/ps5-linux/ps5-linux-loader) for a list of linux supported firmware versions and [here](https://github.com/idlesauce/umtx2) for a list of umtx2 supported firmware versions)

[**Luckfox Lyra Pi RK3506B**](https://www.luckfox.com/Mini-PC/Luckfox-Lyra-Pi) (buy this one for full reboot handling)

[**Luckfox Lyra Plus RK3506G2**](https://amzn.to/4dwrYQ4)

[**Luckfox Pico Plus RV1103**](https://amzn.to/4ut74Hf)

May be compatible with other Luckfox boards that I haven't tested

## What you need

### All boards
- A USB flash drive/USB SSD with PS5 linux already flashed to it (follow through step 3 here: https://github.com/ps5-linux/ps5-linux-loader)
- One of the Luckfox boards listed above
- [A 2GB or larger MicroSD card](https://amzn.to/4n3ffaH)
- [A microSD card reader if you don't have one on your PC](https://amzn.to/4cK22Qv)
- [An ethernet cable (two for the Lyra Pi)](https://amzn.to/4vYXKMB)

### Lyra Pi only
- A PC with Python 3.9+ installed (for the one-time setup script)
- **A USB Bluetooth dongle with a Broadcom chipset** — the Lyra Pi's onboard Bluetooth is not compatible. Known working dongles:
  - [Plugable USB Bluetooth 4.0 Micro Adapter](https://amzn.to/4b8NGaY)
  - [TP-Link UB400](https://amzn.to/4uSu5mx)
- A DualSense controller that's paired to your PS5 (only needed during setup)

## Easy Setup With Pre-built SD Card Images (Lyra Plus & Pico Plus Only)

1. Download the zip file for your Luckfox board from the [releases page](https://github.com/BringusStudios/luckma-ps5/releases). Flash the file to your microSD card using [Balena Etcher](https://etcher.balena.io/). If it bothers you about anything, just continue anyway
2. Insert the microSD card into the Luckfox
3. Plug your linux USB drive into your PS5
4. Connect an ethernet cable between the Luckfox and PS5
5. Connect the Luckfox's USB port to any power source. The USB ports on the PS5 itself work fine

## Hard Setup (Lyra Pi / Manually Prepping an SD Card)

**Lyra Plus/Pico Plus: You'll need to set a static IP on your PC** for the USB RNDIS network interface after connecting it to your PC over USB:

| Board | Set your PC to this IP Address | Subnet Mask |
|---|---|---|
| Lyra Plus | `192.168.123.99` | `255.255.255.0` |
| Pico Plus | `172.32.0.100` | `255.255.255.0` |

Then plug an ethernet cable between the luckfox and the PS5

### Lyra Pi
The Lyra Pi requires a one-time setup via a cross-platform python script. Connect the following first:

| Lyra Pi port | Connect to |
|---|---|
| Middle ethernet port | PS5 LAN port |
| Right ethernet port | Your router or switch (only needed for initial setup) |
| USB-C port | PS5 |
| USB-A port | Bluetooth dongle |
| USB-A port | USB-C cable for connecting your DualSense later |

Create a bootable SD card for your board and then insert it into the board ([Lyra](https://wiki.luckfox.com/Luckfox-Lyra/Getting-Started/Image-flashing), [Pico](https://wiki.luckfox.com/Luckfox-Pico-Plus-Mini/Flash-image/))

Then clone this repo and run the setup script from a local drive:

```sh
git clone https://github.com/BringusStudios/luckma-ps5.git
cd luckma-ps5
python setup_luckfox.py
```

## Usage

### Lyra Pi
Everything is automatic after setup. For the first run after setup I recommend unplugging the PS5 while it's running and then plugging it back in first.

### Lyra Plus & Pico Plus

2. On the PS5 go to **Settings → Network → Set Up Internet Connection**
   - Delete any existing LAN connections and set up a new wired LAN connection, leaving all settings default
3. Open **Settings → User's Guide**
4. Accept the untrusted certificate prompt
5. The Luckfox will automatically detect when the exploit finishes loading and send the Linux loader payload
6. The PS5 will go into rest mode. Wait for the orange light to stop blinking and then press the power button to boot into Linux

To run the jailbreak again after rebooting back to PS5 OS, just repeat steps 3-6. No need to touch the Luckfox, but you are welcome to unplug it after booting into linux.

## How it works

The Luckfox combines a DHCP server, DNS server, web server, and payload sender into one package:

- Serves a DHCP address and spoofs DNS so `manuals.playstation.net` points to the Luckfox
- Hosts the exploit HTTPS page from [umtx2](https://github.com/idlesauce/umtx2)
- Automatically detects when the PS5 exploit triggers and sends the [ps5-linux-loader](https://github.com/ps5-linux/ps5-linux-loader) ELF via socat
- Returns to standby after the payload is sent, ready to run again whenever the PS5 returns to the User's Guide

The Lyra Pi additionally emulates a USB HID keyboard to navigate the PS5 menus automatically, and sends a Bluetooth wake packet afterwards to automatically wake the PS5 from rest mode

## Troubleshooting
*Auto menu navigation seems to be working, but the button timings are off*

You can SSH into /usr/local/bin and edit nav_sequence.py to tweak the timings that are in the SEQUENCE list. The numbers are the time to wait before sending the key in that line.

## Credits

- [idlesauce](https://github.com/idlesauce/umtx2) — umtx2 exploit host (public domain)
- [ps5-linux](https://github.com/ps5-linux/ps5-linux-loader) — ps5-linux-loader (GPL-3.0)
- [socat](http://www.dest-unreach.org/socat/) — socat static ARM binary (GPL-2.0)
- [pywakepsXonbt](https://pypi.org/project/pywakepsXonbt/) — Bluetooth PS5 wake
- [theflow](https://github.com/TheOfficialFloW), [flatz](https://github.com/flatz), [cragson](https://github.com/cragson), [john-tornblom](https://github.com/john-tornblom) and the rest of the ps5 linux folks for the underlying exploit and loader work

## License

[CC BY-NC 4.0](LICENSE) — free to use, modify, and share with attribution. Commercial use is not permitted.
