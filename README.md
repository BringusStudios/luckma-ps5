# luckma-ps5

Automated PS5 Linux boot appliance using a Luckfox single-board computer. Plug in the cables, run the setup script once, and the Luckfox handles everything: serving the exploit page, detecting the PS5, and delivering the Linux loader payload.

**Supported PS5 firmware: 1.00 – 5.50** (via [umtx2](https://github.com/ChendoChap/pOOBs4) exploit)

---

## Supported Boards

| Board | Auto Menu Navigation | Bluetooth Wake | Fully Hands-Free |
|-------|:-------------------:|:--------------:|:----------------:|
| [Luckfox Lyra Pi](https://www.luckfox.com/Mini-PC/Luckfox-Lyra-Pi) | ✅ | ✅ | ✅ |
| [Luckfox Lyra / Lyra Plus](https://www.luckfox.com/Mini-PC/Luckfox-Lyra) | ❌ | ❌ | ❌ |
| [Luckfox Pico Plus](https://www.luckfox.com/Luckfox-Pico/Luckfox-Pico-Plus) | ❌ | ❌ | ❌ |

### Lyra Pi (recommended)
The most feature-rich option. Once set up, it requires **zero interaction** on every boot cycle:
1. PS5 boots into PS5 OS
2. Lyra Pi detects the OS via port scan
3. HID keyboard emulation navigates to the User's Guide automatically
4. Exploit page loads and triggers
5. Linux loader ELF is delivered via socat
6. PS5 boots Linux
7. PS5 enters rest mode, briefly cutting USB power and rebooting the Lyra Pi
8. Lyra Pi boots and sends a Bluetooth wake packet to the PS5
9. Repeat from step 1

### Lyra / Lyra Plus & Pico Plus
These boards serve the exploit page and deliver the loader automatically, but **you still need to manually navigate to Settings → User's Guide** on the PS5 each time to trigger it.

---

## What You Need

### All boards
- PS5 on firmware 1.00–5.50
- MicroSD card (2 GB+)
- Ethernet cable (PS5 ↔ Luckfox)
- PC with Python 3.9+ installed
- USB drive with PS5 Linux installed

### Lyra Pi only (additional)
- **USB Bluetooth dongle with a Broadcom chipset** (required for PS5 wake)
  - Known working: [Plugable USB Bluetooth 4.0 Adapter](https://amzn.to/4b8NGaY)
  - Known working: [TP-Link UB400](https://amzn.to/4uSu5mx)
  - The Lyra Pi's onboard Bluetooth chip is **not compatible** — a USB dongle is required
- DualSense controller (connected via USB to the Lyra Pi during setup only)
- USB hub or spare USB-A port for the dongle

---

## Hardware Setup

### Lyra Pi
Connect the cables as follows before running setup:

| Lyra Pi port | Connect to |
|---|---|
| eth0 (ethernet) | PS5 LAN port |
| eth1 (ethernet) | Your router or switch (for SSH during setup) |
| OTG USB-C port | PS5 USB-A port (for HID keyboard emulation) |
| USB-A port | Bluetooth dongle |
| USB-A port | DualSense controller (setup only) |

The Lyra Pi's LAN IP is assigned by your router via DHCP. You'll enter it when the setup script asks.

### Lyra / Lyra Plus
Connect the ethernet cable between the Lyra Plus's ethernet port and your PS5's LAN port. The Lyra Plus connects to your PC via the USB port (it shows up as a USB RNDIS network adapter).

**Set a static IP on your PC** for the USB RNDIS network interface:
- IP Address: `192.168.123.99`
- Subnet Mask: `255.255.255.0`
- No gateway needed

### Pico Plus
Same as above, but use this static IP on your PC for the RNDIS interface:
- IP Address: `172.32.0.100`
- Subnet Mask: `255.255.255.0`

---

## Setup

### 1. Flash the SD image

Download the SD image for your board from the [Releases](https://github.com/BringusStudios/luckma-ps5/releases) page. Flash it to your microSD card using [Balena Etcher](https://etcher.balena.io/) or [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

### 2. Clone this repo

```sh
git clone https://github.com/BringusStudios/luckma-ps5.git
cd luckma-ps5
```

> **Do not run the setup script from a network drive** (NAS, SMB share, etc.) — the dependency installer requires a local filesystem.

### 3. Run the setup script

```sh
python setup_luckfox.py
```

The script will automatically install its dependencies (`paramiko`, `cryptography`) into a virtual environment on first run.

It will ask you:
1. Which board you're using
2. The device's IP address (Lyra Pi only — check your router's DHCP leases)

**Lyra Pi only:** when prompted, plug your DualSense controller into a USB-A port **on the Lyra Pi** (not your PC). The script will read the Bluetooth MAC addresses directly from the controller and save them automatically.

The script then copies all files to the device, configures it, and reboots it. Setup is complete.

---

## Usage

### Lyra Pi
Everything is automatic after setup. Just make sure all cables are connected and power on the Lyra Pi — it will handle the rest.

If a cycle gets stuck, unplug the Lyra Pi from the PS5's USB port and plug it back in to force a reboot.

### Lyra / Lyra Plus & Pico Plus
1. Power on the Luckfox with the ethernet cable connected to your PS5
2. On the PS5, go to **Settings → User's Guide**
3. The exploit page will load and trigger automatically
4. Wait for Linux to boot

---

## Customizing the Navigation Sequence (Lyra Pi)

The HID navigation sequence is defined in `device/nav_sequence.py`. Each entry is a key code and a duration in seconds.

To record a new sequence interactively, use `device/live_kb.py`:

```sh
# SSH into the Lyra Pi, then:
python3 /path/to/live_kb.py
```

This lets you play back keystrokes in real time and records the timings. Paste the output into `nav_sequence.py`, then re-run `setup_luckfox.py` to deploy the updated sequence.

---

## Credits

- [umtx2](https://github.com/ChendoChap/pOOBs4) — PS5 kernel exploit
- [ps5-linux-loader](https://github.com/ps5-payload-dev/ps5-linux-loader) — ELF loader
- [pywakepsXonbt](https://pypi.org/project/pywakepsXonbt/) — Bluetooth PS5 wake

---

## License

[CC BY-NC 4.0](LICENSE) — free to use, modify, and share with attribution. Commercial use is not permitted.
