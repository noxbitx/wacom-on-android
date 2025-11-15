#!/data/data/com.termux/files/usr/bin/python
"""
Wacom CTL-480 (Intuos PS) Userspace Driver for Android
Reads tablet via libusb and injects as stylus input via uinput
"""
# wacom_driver.py
# Copyright (C) 2025 Noxbit
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import subprocess
import usb.core
import usb.util
import struct
import os
import sys
import time
import ctypes

# uinput setup for input injection

try:
    import fcntl
    UINPUT_PATH = '/dev/uinput'
except ImportError:
    print("Error: Required modules not found")
    sys.exit(1)

# uinput constants

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_ABSBIT = 0x40045567
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502

BUS_USB = 0x03
EV_SYN = 0x00
EV_KEY = 0x01
EV_ABS = 0x03

ABS_X = 0x00
ABS_Y = 0x01
ABS_PRESSURE = 0x18

BTN_TOUCH = 0x14a
BTN_STYLUS = 0x14b
BTN_STYLUS2 = 0x14c
BTN_TOOL_PEN = 0x140

SYN_REPORT = 0

ABS_CNT = 0x40  # ABS_MAX + 1 = 0x3f + 1

# Legacy uinput_user_dev structure for kernels < 4.5
class uinput_user_dev(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 80),
        ("id", ctypes.c_uint16 * 4),  # bustype, vendor, product, version
        ("ff_effects_max", ctypes.c_int),
        ("absmax", ctypes.c_int * ABS_CNT),
        ("absmin", ctypes.c_int * ABS_CNT),
        ("absfuzz", ctypes.c_int * ABS_CNT),
        ("absflat", ctypes.c_int * ABS_CNT)
    ]

class input_event(ctypes.Structure):
    _fields_ = [
        ("time_sec", ctypes.c_long),
        ("time_usec", ctypes.c_long),
        ("type", ctypes.c_uint16),
        ("code", ctypes.c_uint16),
        ("value", ctypes.c_int32)
    ]

# Wacom CTL-480 constants

WACOM_VENDOR_ID = 0x056a
WACOM_PRODUCT_ID = 0x030e

# Tablet specs (CTL-480)

TABLET_MAX_X = 15200
TABLET_MAX_Y = 9500
TABLET_MAX_PRESSURE = 2047

# Screen resolution (adjust for your Tab S2 if needed; confirm with 'wm size' in adb)

SCREEN_WIDTH = 2048
SCREEN_HEIGHT = 1536

# === PRESSURE SCALING ===
# Make pressure easier to reach max (adjust curve)
PRESSURE_EASING = 1.8      # >1.0 = easier max, <1.0 = harder
PRESSURE_OFFSET = 50       # Ignore very light touches
PRESSURE_CLAMP_MIN = 100   # Minimum output when touching

# === UNDO / REDO BUTTONS ===
KEY_LEFTCTRL = 0x1d
KEY_Z = 0x2c
KEY_Y = 0x15

class UInputDevice:
    def __init__(self):
        self.fd = None
        self.setup_device()

    def setup_device(self):
        """Create a virtual stylus input device using legacy API"""
        try:
            self.fd = os.open(UINPUT_PATH, os.O_WRONLY | os.O_NONBLOCK)
        except PermissionError:
            print("Error: Need root access. Run with 'tsu'")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: /dev/uinput not found. Kernel might not support uinput")
            sys.exit(1)
        except OSError as e:
            print(f"Error opening {UINPUT_PATH}: {e}")
            sys.exit(1)

        # Enable event types
        try:
            fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_SYN)
            fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
            fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_ABS)
        except OSError as e:
            print(f"Error setting event bits: {e}")
            sys.exit(1)

        # Enable stylus buttons and tool
        try:
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, BTN_TOUCH)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, BTN_STYLUS)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, BTN_STYLUS2)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, BTN_TOOL_PEN)
            # Enable system keys for Undo/Redo
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, KEY_LEFTCTRL)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, KEY_Z)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, KEY_Y)
        except OSError as e:
            print(f"Error setting key bits: {e}")
            sys.exit(1)

        # Enable absolute axes
        try:
            fcntl.ioctl(self.fd, UI_SET_ABSBIT, ABS_X)
            fcntl.ioctl(self.fd, UI_SET_ABSBIT, ABS_Y)
            fcntl.ioctl(self.fd, UI_SET_ABSBIT, ABS_PRESSURE)
        except OSError as e:
            print(f"Error setting abs bits: {e}")
            sys.exit(1)

        # Setup legacy uinput_user_dev
        try:
            udev = uinput_user_dev()
            udev.name = b'Wacom CTL-480 Userspace'
            udev.id[0] = BUS_USB
            udev.id[1] = WACOM_VENDOR_ID
            udev.id[2] = WACOM_PRODUCT_ID
            udev.id[3] = 1
            udev.ff_effects_max = 0

            # Set abs parameters for X, Y, PRESSURE
            udev.absmin[ABS_X] = 0
            udev.absmax[ABS_X] = SCREEN_WIDTH
            udev.absfuzz[ABS_X] = 0
            udev.absflat[ABS_X] = 0

            udev.absmin[ABS_Y] = 0
            udev.absmax[ABS_Y] = SCREEN_HEIGHT
            udev.absfuzz[ABS_Y] = 0
            udev.absflat[ABS_Y] = 0

            udev.absmin[ABS_PRESSURE] = 0
            udev.absmax[ABS_PRESSURE] = TABLET_MAX_PRESSURE
            udev.absfuzz[ABS_PRESSURE] = 0
            udev.absflat[ABS_PRESSURE] = 0

            # Write the full structure
            os.write(self.fd, bytes(udev))
        except OSError as e:
            print(f"Error writing uinput_user_dev: {e} (Check kernel version or uinput support)")
            sys.exit(1)

        # Create device
        try:
            fcntl.ioctl(self.fd, UI_DEV_CREATE)
            time.sleep(0.2)
            print("✓ Virtual stylus device created")
        except OSError as e:
            print(f"Error creating device: {e}")
            sys.exit(1)

    def send_event(self, ev_type, code, value):
        """Send an input event"""
        current_time = time.time()
        ev = input_event()
        ev.time_sec = int(current_time)
        ev.time_usec = int((current_time - ev.time_sec) * 1000000)
        ev.type = ev_type
        ev.code = code
        ev.value = value
        try:
            os.write(self.fd, bytes(ev))
        except OSError as e:
            print(f"Error sending event: {e}")

    def sync(self):
        """Send SYN event to commit changes"""
        self.send_event(EV_SYN, SYN_REPORT, 0)

    def close(self):
        if self.fd is not None:
            try:
                fcntl.ioctl(self.fd, UI_DEV_DESTROY)
                os.close(self.fd)
                print("✓ Virtual device destroyed")
            except OSError as e:
                print(f"Error closing uinput: {e}")

class WacomDriver:
    def __init__(self):
        self.device = None
        self.endpoint = None
        self.uinput = UInputDevice()
        self.last_x = 0
        self.last_y = 0
        self.in_range = False
        self.button1_pressed = False
        self.button2_pressed = False

    def connect(self):
        """Find and connect to Wacom tablet"""
        print(f"Looking for Wacom tablet {WACOM_VENDOR_ID:04x}:{WACOM_PRODUCT_ID:04x}...")

        self.device = usb.core.find(idVendor=WACOM_VENDOR_ID, idProduct=WACOM_PRODUCT_ID)

        if self.device is None:
            print("Error: Wacom tablet not found!")
            print("Make sure it's plugged in via OTG")
            return False

        print(f"✓ Found: {self.device.manufacturer} {self.device.product}")

        # Detach kernel driver if active
        if self.device.is_kernel_driver_active(0):
            try:
                self.device.detach_kernel_driver(0)
                print("✓ Detached kernel driver")
            except usb.core.USBError as e:
                print(f"Warning: Could not detach kernel driver: {e}")

        # Set configuration
        try:
            self.device.set_configuration()
        except usb.core.USBError:
            pass  # Already configured

        # Get endpoint (usually interface 0, endpoint 1 IN)
        cfg = self.device.get_active_configuration()
        intf = cfg[(0, 0)]
        self.endpoint = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
        )

        if self.endpoint is None:
            print("Error: Could not find input endpoint")
            return False

        print(f"✓ Using endpoint 0x{self.endpoint.bEndpointAddress:02x}")
        return True

    def parse_report(self, data):
        """Parse Wacom HID report"""
        if len(data) < 10:
            return None

        # CTL-480 report format (stylus):
        # [0]: Report ID (usually 0x10 for stylus)
        # [1]: Status byte (in-range, tip switch, buttons)
        # [2-3]: X coordinate (little-endian)
        # [4-5]: Y coordinate (little-endian)
        # [6-7]: Pressure (little-endian)

        report_id = data[0]

        # Only handle stylus reports
        if report_id not in [0x10, 0x02]:
            return None

        status = data[1]
        in_range = bool(status & 0x20)  # Pen in proximity
        tip_switch = bool(status & 0x01)  # Pen touching
        button1 = bool(status & 0x02)  # Lower button
        button2 = bool(status & 0x04)  # Upper button

        # Parse coordinates (little-endian 16-bit)
        x = struct.unpack('<H', bytes(data[2:4]))[0]
        y = struct.unpack('<H', bytes(data[4:6]))[0]
        pressure = struct.unpack('<H', bytes(data[6:8]))[0]

        return {
            'in_range': in_range,
            'tip_switch': tip_switch,
            'button1': button1,
            'button2': button2,
            'x': x,
            'y': y,
            'pressure': pressure
        }

    def map_coordinates(self, tablet_x, tablet_y):
        """Map tablet coordinates to screen coordinates"""
        screen_x = int((tablet_x / TABLET_MAX_X) * SCREEN_WIDTH)
        screen_y = int((tablet_y / TABLET_MAX_Y) * SCREEN_HEIGHT)

        # Clamp to screen bounds
        screen_x = max(0, min(SCREEN_WIDTH, screen_x))
        screen_y = max(0, min(SCREEN_HEIGHT, screen_y))

        return screen_x, screen_y

    def process_event(self, report):
        """Process parsed report and send input events"""
        if report is None:
            return

        # Handle proximity change
        if report['in_range'] != self.in_range:
            self.uinput.send_event(EV_KEY, BTN_TOOL_PEN, 1 if report['in_range'] else 0)
            self.in_range = report['in_range']
            status = "in range" if self.in_range else "out of range"
            print(f"Stylus {status}")
            self.uinput.sync()

        if self.in_range:
            # === MAP COORDINATES ===
            screen_x, screen_y = self.map_coordinates(report['x'], report['y'])
            self.uinput.send_event(EV_ABS, ABS_X, screen_x)
            self.uinput.send_event(EV_ABS, ABS_Y, screen_y)

            # === PRESSURE SCALING (EASIER MAX) ===
            raw_pressure = report['pressure']
            if raw_pressure > PRESSURE_OFFSET:
                scaled = (raw_pressure - PRESSURE_OFFSET) / (TABLET_MAX_PRESSURE - PRESSURE_OFFSET)
                scaled = scaled ** (1.0 / PRESSURE_EASING)  # Inverse power curve
                pressure_out = int(scaled * TABLET_MAX_PRESSURE)
                pressure_out = max(PRESSURE_CLAMP_MIN, pressure_out)
            else:
                pressure_out = 0
            self.uinput.send_event(EV_ABS, ABS_PRESSURE, pressure_out)

            # === TOUCH & TIP ===
            self.uinput.send_event(EV_KEY, BTN_TOUCH, 1 if report['tip_switch'] else 0)

            # === STYLUS BUTTONS → UNDO / REDO ===
            # Button 1 (lower): Undo (Ctrl+Z)
            # Button 2 (upper): Redo (Ctrl+Y)
            if report['button1'] and not self.button1_pressed:
                self.send_key_combo(KEY_LEFTCTRL, KEY_Z)
            if report['button2'] and not self.button2_pressed:
                self.send_key_combo(KEY_LEFTCTRL, KEY_Y)

            # Update button state
            self.button1_pressed = report['button1']
            self.button2_pressed = report['button2']

            # Always send BTN_STYLUS state (for apps that read it)
            self.uinput.send_event(EV_KEY, BTN_STYLUS, 1 if report['button1'] else 0)
            self.uinput.send_event(EV_KEY, BTN_STYLUS2, 1 if report['button2'] else 0)

            self.uinput.sync()

        else:
            # Out of range: release everything
            self.uinput.send_event(EV_ABS, ABS_PRESSURE, 0)
            self.uinput.send_event(EV_KEY, BTN_TOUCH, 0)
            self.uinput.send_event(EV_KEY, BTN_STYLUS, 0)
            self.uinput.send_event(EV_KEY, BTN_STYLUS2, 0)

            self.uinput.sync()

    def send_key_combo(self, mod_key, key):
        """Send key + modifier (e.g., Ctrl+Z)"""
        self.uinput.send_event(EV_KEY, mod_key, 1)
        self.uinput.send_event(EV_KEY, key, 1)
        self.uinput.sync()
        time.sleep(0.01)
        self.uinput.send_event(EV_KEY, key, 0)
        self.uinput.send_event(EV_KEY, mod_key, 0)
        self.uinput.sync()

    def run(self):
        """Main event loop"""
        print("\n=== Wacom Driver Active ===")
        print("Move your stylus on the tablet!")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                try:
                    # Read data from tablet (timeout 100ms)
                    data = self.endpoint.read(self.endpoint.wMaxPacketSize, timeout=100)

                    # Parse and process
                    report = self.parse_report(data)
                    self.process_event(report)

                except usb.core.USBTimeoutError:
                    continue
                except usb.core.USBError as e:
                    print(f"USB Error: {e}")
                    break

        except KeyboardInterrupt:
            print("\n\nStopping driver...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.uinput.close()
        if self.device:
            usb.util.dispose_resources(self.device)
        print("✓ Cleaned up")

def main():
    print("=== Wacom CTL-480 Userspace Driver ===\n")

    # Check if running as root
    if os.geteuid() != 0:
        print("Error: This script needs root access")
        print("Run with: tsu 'python wacom_driver.py'")
        return 1

    driver = WacomDriver()

    if not driver.connect():
        return 1

    driver.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
