import time
import sys
from nav_sequence import KEY_CODES, SEQUENCE

HID_DEVICE = '/dev/hidg0'
LOG_FILE = '/tmp/nav_log.txt'

def log(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')
    print(msg)

def send_key(hid, keycode, modifier=0):
    press = bytes([modifier, 0, keycode, 0, 0, 0, 0, 0])
    release = bytes([0, 0, 0, 0, 0, 0, 0, 0])
    hid.write(press)
    hid.flush()
    time.sleep(0.05)
    hid.write(release)
    hid.flush()

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
    open(LOG_FILE, 'w').close()  # clear previous log
    log("Starting PS5 menu navigation...")
    with open(HID_DEVICE, 'wb', buffering=0) as hid:
        for delay, key_name in SEQUENCE:
            countdown(delay, key_name)
            keycode = KEY_CODES[key_name]
            send_key(hid, keycode)
            log(f"[{time.strftime('%H:%M:%S')}] Sent key: {key_name}")
    log("Navigation complete.")

if __name__ == '__main__':
    play_navigation()
