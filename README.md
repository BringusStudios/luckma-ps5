# luckma-ps5
Zero config automated jailbreak and linux loader for linux-compatible PS5s utilizing the Luckfox Pico Plus or Lyra Plus SBC.

# [Big Obvious Download Button Here](https://github.com/BringusStudios/luckma-ps5/releases)

Online shopping links listed here are affiliate links that generate me a small revenue when purchased from

If you want to get into the weeds and change things/wanna read the source code, flash the img to your microSD card and SSH into the Luckfox and find the main script at /usr/local/bin/ps5-jailbreak.sh

## Compatibility

**A linux-compatible & umtx2 compatible PS5** (check [here](https://github.com/ps5-linux/ps5-linux-loader) for a list of linux supported firmware versions and [here](https://github.com/idlesauce/umtx2) for a list of umtx2 supported firmware versions)

[**Luckfox Lyra Plus RK3506G2**](https://amzn.to/4dwrYQ4)

[**Luckfox Pico Plus RV1103**](https://amzn.to/4ut74Hf)

May be compatible with other luckfox boards that I haven't tested

## What you need

- A USB flash drive/USB SSD with PS5 linux already flashed to it (follow through step 3 here: https://github.com/ps5-linux/ps5-linux-loader)
- One of the Luckfox boards listed above (the Lyra is technically better, but for this use case it doesn't matter)
- [A 2GB or larger MicroSD card](https://amzn.to/4n3ffaH)
- [A microSD card reader if you don't have one on your PC](https://amzn.to/4cK22Qv)
- [An ethernet cable](https://amzn.to/4vYXKMB)

## Setup

1. Download the .7z file for your Luckfox board and extract the .img file somewhere on your PC. Flash the .img file to your microSD card using [Balena Etcher](https://etcher.balena.io/) or [Win32DiskImager](https://win32diskimager.org/). If it bothers you about anything, just continue anyway
2. Insert the microSD card into the Luckfox
3. Plug your linux USB drive into your PS5
4. Connect an ethernet cable between the Luckfox and PS5
5. Connect the Luckfox's USB port to any power source. The USB ports on the PS5 itself work fine

## Usage

2. On the PS5 go to **Settings → Network → Set Up Internet Connection**
   - Delete any existing LAN connections and set up a new wired LAN connection, leaving all settings default
3. Open **Settings → User Guide**
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
- Returns to standby after the payload is sent to be ready to run again whenever the PS5 returns to the User Guide

## Credits

- [idlesauce](https://github.com/idlesauce/umtx2) — umtx2 exploit host (public domain)
- [ps5-linux](https://github.com/ps5-linux/ps5-linux-loader) — ps5-linux-loader (GPL-3.0)
- [socat](http://www.dest-unreach.org/socat/) — socat static ARM binary (GPL-2.0)
- [theflow](https://github.com/TheOfficialFloW), [flatz](https://github.com/flatz), [cragson](https://github.com/cragson), [john-tornblom](https://github.com/john-tornblom) and the rest of the ps5 linux folks for the underlying exploit and loader work

## License

The scripts in this project are released under MIT. Bundled third party components retain their respective licenses as noted in Credits above.
