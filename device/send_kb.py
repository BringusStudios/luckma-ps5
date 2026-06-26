#!/usr/bin/env python3
import time
import sys

#ps5 takes about 15 seconds from usb ports powering up to waiting for input

HID_DEVICE = '/dev/hidg0'

KEY_CODES = {
    'ENTER': 0x28,
    'ESC': 0x29,
    'BACKSPACE': 0x2a,
    'TAB': 0x2b,
    'SPACE': 0x2c,
    'UP': 0x52,
    'DOWN': 0x51,
    'RIGHT': 0x4f,
    'LEFT': 0x50,
    'PAGE_UP': 0x4b,
    'PAGE_DOWN': 0x4e,
    'A': 0x04, 'B': 0x05, 'C': 0x06, 'D': 0x07,
    'E': 0x08, 'F': 0x09, 'G': 0x0a, 'H': 0x0b,
    'I': 0x0c, 'J': 0x0d, 'K': 0x0e, 'L': 0x0f,
    'M': 0x10, 'N': 0x11, 'O': 0x12, 'P': 0x13,
    'Q': 0x14, 'R': 0x15, 'S': 0x16, 'T': 0x17,
    'U': 0x18, 'V': 0x19, 'W': 0x1a, 'X': 0x1b,
    'Y': 0x1c, 'Z': 0x1d,
}

def send_key(hid, keycode, modifier=0):
    press = bytes([modifier, 0, keycode, 0, 0, 0, 0, 0])
    release = bytes([0, 0, 0, 0, 0, 0, 0, 0])
    hid.write(press)
    hid.flush()
    time.sleep(0.05)
    hid.write(release)
    hid.flush()

SEQUENCE = [
    (0.000, 'ENTER'),
    (9.000, 'ENTER'),
    (2.996, 'ENTER'),
    (3.000, 'UP'),
    (0.241, 'RIGHT'),
    (0.29,  'RIGHT'),
    (0.339, 'RIGHT'),
    (0.553, 'ENTER'),
    (1.902, 'UP'),
    (0.353, 'UP'),
    (0.382, 'ENTER'),
    (1.107, 'ENTER'),
    (0.761, 'ENTER'),
    (2.723, 'ENTER'),
]

def countdown(seconds, next_key):
    if seconds <= 0:
        return
    step = 0.1
    remaining = seconds
    while remaining > 0:
        sys.stdout.write(f"\r  next key '{next_key}' in {remaining:4.1f}s ")
        sys.stdout.flush()
        sleep_time = min(step, remaining)
        time.sleep(sleep_time)
        remaining -= sleep_time
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()

def play_navigation():
    print("Starting PS5 menu navigation...")
    with open(HID_DEVICE, 'wb', buffering=0) as hid:
        for delay, key_name in SEQUENCE:
            countdown(delay, key_name)
            keycode = KEY_CODES[key_name]
            send_key(hid, keycode)
            print(f"Sent key: {key_name}")
    print("Navigation complete.")

if __name__ == '__main__':
    play_navigation()