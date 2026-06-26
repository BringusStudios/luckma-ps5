# luckma-ps5

Zero config automated jailbreak and linux loader for linux-compatible PS5s utilizing a Luckfox SBC.

# [Big Obvious Download Button Here](https://github.com/BringusStudios/luckma-ps5/releases)

Online shopping links listed here are affiliate links that generate me a small revenue when purchased from

If you want to get into the weeds and change things/wanna read the source code, find the main script at `device/` in this repo, or SSH into the Luckfox and find it at `/usr/local/bin/ps5-jailbreak.sh`

## Compatibility

**A linux-compatible & umtx2 compatible PS5** (check [here](https://github.com/ps5-linux/ps5-linux-loader) for a list of linux supported firmware versions and [here](https://github.com/idlesauce/umtx2) for a list of umtx2 supported firmware versions)

[**Luckfox Lyra Pi RK3506B**](https://www.luckfox.com/Mini-PC/Luckfox-Lyra-Pi) — most feature-rich, fully hands-free

[**Luckfox Lyra Plus RK3506G2**](https://amzn.to/4dwrYQ4)

[**Luckfox Pico Plus RV1103**](https://amzn.to/4ut74Hf)

May be compatible with other Luckfox boards that I haven't tested

## What you need

### All boards
- A USB flash drive/USB SSD with PS5 linux already flashed to it (follow through step 3 here: https://github.com/ps5-linux/ps5-linux-loader)
- One of the Luckfox boards listed above
- [A 2GB or larger MicroSD card](https://amzn.to/4n3ffaH)
- [A microSD card reader if you don't have one on your PC](https://amzn.to/4cK22Qv)
- [An ethernet cable](https://amzn.to/4vYXKMB)

### Lyra Pi only (additional)
- A PC with Python 3.9+ installed (for the one-time setup script)
- **A USB Bluetooth dongle with a Broadcom chipset** — the Lyra Pi's onboard Bluetooth is not compatible. Known working dongles:
  - [Plugable USB Bluetooth 4.0 Micro Adapter](https://amzn.to/4b8NGaY)
  - [TP-Link UB400](https://amzn.to/4uSu5mx)
- A DualSense controller connected via USB to the Lyra Pi (one-time setup only)

## Setup

### Lyra Plus & Pico Plus
1. Download the .7z file for your Luckfox board from the [releases page](https://github.com/BringusStudios/luckma-ps5/releases) and extract the .img file somewhere on your PC. Flash the .img file to your microSD card using [Balena Etcher](https://etcher.balena.io/) or [Win32DiskImager](https://win32diskimager.org/). If it bothers you about anything, just continue anyway
2. Insert the microSD card into the Luckfox
3. Plug your linux USB drive into your PS5
4. Connect an ethernet cable between the Luckfox and PS5
5. Connect the Luckfox's USB port to any power source. The USB ports on the PS5 itself work fine

**You'll also need to set a static IP on your PC** for the USB RNDIS network interface that appears when the Luckfox is plugged in:

| Board | IP Address | Subnet Mask |
|---|---|---|
| Lyra / Lyra Plus | `192.168.123.99` | `255.255.255.0` |
| Pico Plus | `172.32.0.100` | `255.255.255.0` |

### Lyra Pi
The Lyra Pi requires a one-time setup from your PC. Connect everything before running it:

| Lyra Pi port | Connect to |
|---|---|
| eth0 (ethernet) | PS5 LAN port |
| eth1 (ethernet) | Your router or switch |
| OTG USB-C port | PS5 USB-A port |
| USB-A port | Bluetooth dongle |
| USB-A port | DualSense controller (setup only) |

Then clone this repo and run the setup script from a local drive (not a network share):

```sh
git clone https://github.com/BringusStudios/luckma-ps5.git
cd luckma-ps5
python setup_luckfox.py
```

The script installs its own dependencies automatically. When prompted, plug your DualSense into a USB-A port **on the Lyra Pi** — the script reads the Bluetooth MAC addresses directly from the controller. Setup takes a few minutes and reboots the device when done.

## Usage

### Lyra Pi
Everything is automatic after setup — just make sure all cables are connected and power it on.

The full hands-free cycle:
1. PS5 boots into PS5 OS
2. Lyra Pi detects PS5 OS and navigates to the User's Guide automatically via HID keyboard emulation
3. Exploit page loads and triggers
4. Linux loader ELF is sent via socat
5. PS5 goes into rest mode, cutting USB power and rebooting the Lyra Pi
6. Lyra Pi boots and sends a Bluetooth wake packet to the PS5
7. Repeat from step 1

### Lyra Plus & Pico Plus

2. On the PS5 go to **Settings → Network → Set Up Internet Connection**
   - Delete any existing LAN connections and set up a new wired LAN connection, leaving all settings default
3. Open **Settings → User's Guide**
4. Accept the untrusted certificate prompt
5. Press the **Jailbreak** button on the page that loads
6. The Luckfox will automatically detect when the exploit finishes loading and send the Linux loader payload
7. The PS5 will go into rest mode. Wait for the orange light to stop blinking and then press the power button to boot into Linux

To run the jailbreak again after rebooting back to PS5 OS, just repeat steps 3-7. No need to touch the Luckfox, but you are welcome to unplug it after booting into linux.

## How it works

The Luckfox combines a DHCP server, DNS server, web server, and payload sender into one package:

- Serves a DHCP address and spoofs DNS so `manuals.playstation.net` points to the Luckfox
- Hosts the exploit HTTPS page from [umtx2](https://github.com/idlesauce/umtx2)
- Automatically detects when the PS5 exploit triggers and sends the [ps5-linux-loader](https://github.com/ps5-linux/ps5-linux-loader) ELF via socat
- Returns to standby after the payload is sent, ready to run again whenever the PS5 returns to the User's Guide

The Lyra Pi additionally emulates a USB HID keyboard to navigate the PS5 menus automatically, and sends a Bluetooth wake packet on every boot so the PS5 wakes from rest mode and starts the cycle over.

## Credits

- [idlesauce](https://github.com/idlesauce/umtx2) — umtx2 exploit host (public domain)
- [ps5-linux](https://github.com/ps5-linux/ps5-linux-loader) — ps5-linux-loader (GPL-3.0)
- [socat](http://www.dest-unreach.org/socat/) — socat static ARM binary (GPL-2.0)
- [pywakepsXonbt](https://pypi.org/project/pywakepsXonbt/) — Bluetooth PS5 wake
- [theflow](https://github.com/TheOfficialFloW), [flatz](https://github.com/flatz), [cragson](https://github.com/cragson), [john-tornblom](https://github.com/john-tornblom) and the rest of the ps5 linux folks for the underlying exploit and loader work

## License

[CC BY-NC 4.0](LICENSE) — free to use, modify, and share with attribution. Commercial use is not permitted.
