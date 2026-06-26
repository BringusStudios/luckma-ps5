"""Patches pyusb to find libusb by explicit path.

This image has no ldconfig/ld.so.cache, so pyusb's default backend discovery
(ctypes.util.find_library) can't locate /usr/lib/libusb-1.0.so.0 even though
it's present and loads fine via a direct ctypes.CDLL() call. Import this
before anything that calls usb.core.find() (e.g. pywakepsx_on_bt's
extract_psx_bt_macs()).
"""
import usb.backend.libusb1 as _libusb1
import usb.core as _usb_core

_backend = _libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so.0")
_orig_find = _usb_core.find


def _patched_find(*args, **kwargs):
    kwargs.setdefault("backend", _backend)
    return _orig_find(*args, **kwargs)


_usb_core.find = _patched_find
