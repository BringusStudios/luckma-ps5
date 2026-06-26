#!/usr/bin/env python3
"""Cross-platform setup script for the luckma-ps5 Luckfox devices.

Replaces setup_luckfox.ps1. Uses paramiko for SSH/SFTP instead of shelling
out to ssh/scp/ssh-keygen so this runs the same way on Windows, macOS, and
Linux.
"""
from __future__ import annotations

import getpass
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import paramiko
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except ImportError:
    import os
    venv_dir = Path.home() / ".local" / "share" / "luckma-ps5" / ".venv"
    venv_python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    print("[*] Installing required dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    except subprocess.CalledProcessError:
        ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"[!] Failed to create virtual environment.")
        print(f"    On Debian/Ubuntu, run:  sudo apt install python{ver}-venv")
        print(f"    Then re-run this script.")
        sys.exit(1)
    subprocess.run([str(venv_python), "-m", "pip", "install", "--quiet",
                    "paramiko", "cryptography"], check=True)
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)

REPO_DIR = Path(__file__).resolve().parent
DEVICE_DIR = REPO_DIR / "device"
KEY_PATH = Path.home() / ".ssh" / "luckfox_id_ed25519"

# choice -> (label, fixed IP or None to prompt, base path on device)
DEVICES = {
    "1": ("Luckfox Pico Plus", "172.32.0.93", "/userdata"),
    "2": ("Luckfox Lyra / Lyra Plus", "192.168.123.100", "/root"),
    "3": ("Luckfox Lyra Pi", None, "/root"),
}


def ensure_ssh_key() -> None:
    if KEY_PATH.exists():
        return
    print("[*] Generating SSH key for passwordless Luckfox setup...")
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    private_key = Ed25519PrivateKey.generate()
    KEY_PATH.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    KEY_PATH.chmod(0o600)
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    KEY_PATH.with_suffix(".pub").write_bytes(pub_bytes + b" luckma-ps5-setup\n")


def trust_key(client: paramiko.SSHClient) -> None:
    pub = KEY_PATH.with_suffix(".pub").read_text().strip()
    cmd = (
        "mkdir -p /root/.ssh && chmod 700 /root/.ssh && touch /root/.ssh/authorized_keys && "
        f"grep -qxF '{pub}' /root/.ssh/authorized_keys || echo '{pub}' >> /root/.ssh/authorized_keys; "
        "chmod 600 /root/.ssh/authorized_keys"
    )
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.read()


def connect(ip: str) -> paramiko.SSHClient:
    import socket
    pkey = paramiko.Ed25519Key.from_private_key_file(str(KEY_PATH))
    while True:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(ip, username="root", pkey=pkey, timeout=10)
            return client
        except (paramiko.AuthenticationException, paramiko.SSHException):
            client.connect(ip, username="root", password=getpass.getpass(
                f"SSH password for root@{ip} (key not yet trusted): "), timeout=10)
            trust_key(client)
            return client
        except (TimeoutError, socket.timeout, OSError):
            print(f"[!] Could not reach {ip} — device may still be booting.")
            answer = input("    Retry? [Y/n]: ").strip().lower()
            if answer == "n":
                sys.exit(1)


def run(client: paramiko.SSHClient, cmd: str, check: bool = True) -> str:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    if err:
        print(err, end="" if err.endswith("\n") else "\n", file=sys.stderr)
    if check and code != 0:
        raise RuntimeError(f"Command failed ({code}): {cmd}")
    return out


def put_file(client: paramiko.SSHClient, local: Path, remote: str) -> None:
    sftp = client.open_sftp()
    try:
        sftp.put(str(local), remote)
    finally:
        sftp.close()


def put_dir(client: paramiko.SSHClient, local_dir: Path, remote_dir: str) -> None:
    sftp = client.open_sftp()
    try:
        run(client, f"mkdir -p {remote_dir}")
        for item in sorted(local_dir.rglob("*")):
            rel = item.relative_to(local_dir).as_posix()
            remote_path = f"{remote_dir}/{rel}"
            if item.is_dir():
                run(client, f"mkdir -p {remote_path}")
            else:
                sftp.put(str(item), remote_path)
    finally:
        sftp.close()


def detect_dualsense_macs(client: paramiko.SSHClient) -> list[dict]:
    """Run pywakepsx_on_bt's controller scan on-device, filtered to DualSense only."""
    code = (
        "import usb_backend_fix; import json; "
        "from pywakepsx_on_bt import extract_psx_bt_macs; "
        "print(json.dumps(extract_psx_bt_macs()))"
    )
    out = run(client, f"cd /usr/local/bin && python3 -c \"{code}\"")
    results = json.loads(out.strip().splitlines()[-1])
    others = [r for r in results if r.get("controller_type") != "dualsense"]
    if others:
        kinds = ", ".join(sorted({r["controller_type"] for r in others}))
        print(f"[!] Detected non-DualSense controller(s) ({kinds}) -- ignoring. A DualSense is required.")
    return [r for r in results if r.get("controller_type") == "dualsense"]


def setup_bluetooth_wake(client: paramiko.SSHClient) -> None:
    print()
    print("Bluetooth wake setup (DualSense controller required)")

    wheel_dir = DEVICE_DIR / "wheels"
    whls = list(wheel_dir.glob("*.whl")) if wheel_dir.exists() else []
    if not whls:
        print("[*] Downloading pywakepsx-on-bt wheels...")
        wheel_dir.mkdir(exist_ok=True)
        subprocess.run(
            [sys.executable, "-m", "pip", "download", "--no-deps", "-d", str(wheel_dir),
             "pywakepsx-on-bt", "pyusb"],
            check=True,
        )
        whls = list(wheel_dir.glob("*.whl"))

    print("[*] Installing libusb on device (needed for MAC detection)...")
    libusb_lib = DEVICE_DIR / "lib" / "libusb-1.0.so.0.3.0"
    run(client, "mkdir -p /usr/lib")
    put_file(client, libusb_lib, "/usr/lib/libusb-1.0.so.0.3.0")
    run(client, "ln -sf libusb-1.0.so.0.3.0 /usr/lib/libusb-1.0.so.0 && "
                "ln -sf libusb-1.0.so.0.3.0 /usr/lib/libusb-1.0.so")

    print("[*] Staging pywakepsx-on-bt on device for MAC detection... this can take a long time")
    run(client, "mkdir -p /tmp/wheels /usr/local/bin")
    put_file(client, DEVICE_DIR / "usb_backend_fix.py", "/usr/local/bin/usb_backend_fix.py")
    sftp = client.open_sftp()
    try:
        for whl in whls:
            sftp.put(str(whl), f"/tmp/wheels/{whl.name}")
    finally:
        sftp.close()
    run(client, "python3 -m ensurepip >/dev/null 2>&1 || true", check=False)
    run(client, "pip3 install --quiet --no-index --find-links /tmp/wheels pywakepsx-on-bt")

    print()
    print("Plug your DualSense controller into a USB-A port on the Lyra Pi now.")
    input("Press Enter once it's connected... ")

    results: list[dict] = []
    for attempt in range(1, 4):
        results = detect_dualsense_macs(client)
        if results:
            break
        print("[!] No DualSense controller detected. Make sure it's plugged into the Lyra Pi (not your PC).")
        if attempt < 3:
            input("Press Enter to try again... ")
    if not results:
        print("[!] Could not detect a DualSense controller after 3 attempts. Aborting.")
        sys.exit(1)

    if len(results) > 1:
        print(f"[!] Multiple DualSense controllers detected ({len(results)}); using the first one.")
    ds_mac = results[0]["dsx_mac"]
    ps_mac = results[0]["psx_mac"]
    print(f"[*] Detected controller MAC: {ds_mac}")
    print(f"[*] Detected PS5 MAC: {ps_mac}")

    bt_config = {"type": "dualsense", "dsbt_address": ds_mac, "psXbt_address": ps_mac}
    (DEVICE_DIR / "bt_config.json").write_text(json.dumps(bt_config))
    print("[*] Saved bt_config.json")


def main() -> None:
    print("Select your Luckfox device:")
    for choice, (label, _, _) in DEVICES.items():
        print(f"{choice}) {label}")
    choice = input("Enter 1, 2, or 3: ").strip()
    if choice not in DEVICES:
        print("[!] Invalid selection.")
        sys.exit(1)

    _, ip, base = DEVICES[choice]
    if ip is None:
        ip = input("Enter the Lyra Pi's IP address: ").strip()
    print(f"[*] Using {ip}")

    ensure_ssh_key()
    print("[*] Ensuring SSH key is trusted on device... When prompted for a password, enter luckfox")
    client = connect(ip)

    if choice == "3":
        setup_bluetooth_wake(client)

    print("[*] Stopping services and cleaning up...")
    put_file(client, DEVICE_DIR / "remote_stop.sh", "/tmp/remote_stop.sh")
    run(client, "chmod +x /tmp/remote_stop.sh && /tmp/remote_stop.sh")

    print("[*] Syncing device clock...")
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    run(client, f"date -u -s '{now_utc}'")

    print("[*] Copying files...")
    put_dir(client, DEVICE_DIR / "umtx2", f"{base}/umtx2")
    put_file(client, DEVICE_DIR / "ps5-linux-loader.elf", f"{base}/ps5-linux-loader.elf")
    put_file(client, DEVICE_DIR / "socat", f"{base}/socat")
    put_file(client, DEVICE_DIR / "remote_setup.sh", f"{base}/remote_setup.sh")

    if choice == "3":
        run(client, "mkdir -p /usr/local/bin /tmp/wheels")
        put_file(client, DEVICE_DIR / "bt_config.json", "/usr/local/bin/bt_config.json")
        put_file(client, DEVICE_DIR / "bt_wake.py", "/usr/local/bin/bt_wake.py")
        put_file(client, DEVICE_DIR / "usb_backend_fix.py", "/usr/local/bin/usb_backend_fix.py")
        put_file(client, DEVICE_DIR / "ps5_os_detect.py", "/usr/local/bin/ps5_os_detect.py")
        put_file(client, DEVICE_DIR / "hid_navigate.py", "/usr/local/bin/hid_navigate.py")
        put_file(client, DEVICE_DIR / "nav_sequence.py", "/usr/local/bin/nav_sequence.py")
        put_file(client, DEVICE_DIR / "usb_f_hid.ko", f"{base}/usb_f_hid.ko")
        put_file(client, DEVICE_DIR / "lib" / "libusb-1.0.so.0.3.0", "/tmp/libusb-1.0.so.0.3.0")
        for whl in (DEVICE_DIR / "wheels").glob("*.whl"):
            put_file(client, whl, f"/tmp/wheels/{whl.name}")

    ps5_eth = "eth1" if choice == "2" else "eth0"
    print("[*] Running setup... this can take a long time")
    run(client, f"chmod +x {base}/remote_setup.sh && {base}/remote_setup.sh {ps5_eth}")

    print("[*] Done. Luckfox is rebooting. Feel free to unplug your controller now.\nIf auto-natigation fails to start the user guide, unplug your PS5 from the wall while it's running and then turn it on.")
    client.close()


if __name__ == "__main__":
    main()
