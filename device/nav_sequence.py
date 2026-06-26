# Edit timings here if your PS5 menu navigation needs adjustment.
# Each entry is (delay_in_seconds, key_name)
# delay = how long to wait AFTER the previous key before sending this one

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

SEQUENCE = [
    (2.269, 'ENTER'),  # '\r'
    (7.197, 'ENTER'),  # '\r'
    (1.83, 'ENTER'),  # '\r'
    (2.177, 'ENTER'),  # '\r'
    (1.100, 'UP'),  # '\x1b[A'
    (0.386, 'RIGHT'),  # '\x1b[C'
    (0.204, 'RIGHT'),  # '\x1b[C'
    (0.292, 'RIGHT'),  # '\x1b[C'
    (0.341, 'ENTER'),  # '\r'
    (1.31, 'UP'),  # '\x1b[A'
    (0.209, 'UP'),  # '\x1b[A'
    (0.212, 'ENTER'),  # '\r'
    (0.816, 'ENTER'),  # '\r'
    (0.207, 'ENTER'),  # '\r'
    (2.669, 'ENTER'),  # '\r'
]
