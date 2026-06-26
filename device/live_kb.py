#!/usr/bin/env python3
import tty
import sys
import termios
import time

KEY_MAP = {
    '\r': 0x28, '\n': 0x28, '\x7f': 0x2a,
    '\x1b[A': 0x52, '\x1b[B': 0x51, '\x1b[C': 0x4f, '\x1b[D': 0x50,
    '\x1b[5~': 0x4b, '\x1b[6~': 0x4e,
    ' ': 0x2c, '\t': 0x2b, '\x1b': 0x29,
    'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07,
    'e': 0x08, 'f': 0x09, 'g': 0x0a, 'h': 0x0b,
    'i': 0x0c, 'j': 0x0d, 'k': 0x0e, 'l': 0x0f,
    'm': 0x10, 'n': 0x11, 'o': 0x12, 'p': 0x13,
    'q': 0x14, 'r': 0x15, 's': 0x16, 't': 0x17,
    'u': 0x18, 'v': 0x19, 'w': 0x1a, 'x': 0x1b,
    'y': 0x1c, 'z': 0x1d,
}

HID_DEVICE = '/dev/hidg0'
LOG_FILE = '/tmp/keystroke_log.txt'

def read_key():
    ch = sys.stdin.read(1)
    if ch == '\x1b':
        try:
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            seq = ch + ch2 + ch3
            if ch3 in ('5', '6'):
                ch4 = sys.stdin.read(1)
                seq += ch4
            return seq
        except:
            return ch
    return ch

def main():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    log = []
    start_time = time.time()
    print("PS5 Keyboard Passthrough - press Ctrl+C to exit and save log")
    try:
        tty.setraw(fd)
        with open(HID_DEVICE, 'wb', buffering=0) as hid:
            while True:
                key = read_key()
                if key == '\x03':
                    break
                elapsed = round(time.time() - start_time, 3)
                if key in KEY_MAP:
                    keycode = KEY_MAP[key]
                    press = bytes([0, 0, keycode, 0, 0, 0, 0, 0])
                    release = bytes([0, 0, 0, 0, 0, 0, 0, 0])
                    hid.write(press)
                    hid.flush()
                    time.sleep(0.05)
                    hid.write(release)
                    hid.flush()
                    log.append((elapsed, key, keycode))
                    sys.stdout.write(f'\r[{elapsed}s] sent: {repr(key)} (0x{keycode:02x})\n')
                    sys.stdout.flush()
                else:
                    sys.stdout.write(f'\r[{elapsed}s] unknown: {repr(key)}\n')
                    sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        with open(LOG_FILE, 'w') as f:
            f.write("time,key,keycode\n")
            for t, k, kc in log:
                f.write(f"{t},{repr(k)},0x{kc:02x}\n")
        print(f"\nLog saved to {LOG_FILE}")
        print("\nReplay sequence:")
        prev_t = 0
        for t, k, kc in log:
            delay = round(t - prev_t, 3)
            print(f"  sleep({delay}) + send_key(0x{kc:02x})  # {repr(k)}")
            prev_t = t

if __name__ == '__main__':
    main()