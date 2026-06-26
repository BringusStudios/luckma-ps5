#!/usr/bin/env python3
import json
from pywakepsx_on_bt import wake_psx, detect_strategy

BT_CONFIG_FILE = '/usr/local/bin/bt_config.json'
ADAPTER_INDEX = 1  # hci1 = USB dongle (hci0 is the unsupported onboard chip)
ADAPTER = f'hci{ADAPTER_INDEX}'

def main():
    with open(BT_CONFIG_FILE, 'r') as f:
        config = json.load(f)

    psx_mac = config['psXbt_address']
    dsx_mac = config['dsbt_address']

    print(f"Sending BT wake to {psx_mac} via {ADAPTER}...")
    strategy = detect_strategy(ADAPTER_INDEX)
    result = wake_psx(dsx_mac, psx_mac, adapter=ADAPTER, spoof_strategy=strategy)
    print(f"Status: {result.status_text} (0x{result.status_code:02X})")

if __name__ == '__main__':
    main()
