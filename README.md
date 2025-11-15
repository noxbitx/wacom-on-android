You’re absolutely right — my bad! Here’s the clean, copy-paste-ready README.md with perfect formatting, no blending, and 100% selectable.

`README.md` — Professional & Copy-Paste Ready
# Wacom Android Userspace Driver

### *Turn any rooted Android tablet into a full Wacom Intuos*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Android 14 Tested](https://img.shields.io/badge/Android-14%20Tested-green)](#)

> **No kernel modules. No recompilation. Full hover, pressure, and undo/redo.**  
> Works on **Samsung Galaxy Tab S2 (LineageOS 21)** — and any rooted Android with `/dev/uinput`.

---

## Features

| Feature                | Status    |
|------------------------|-----------|
| Hover cursor           | Supported |
| 2048-level pressure    | Supported (tunable) |
| Tip click & barrel buttons | Supported |
| Button 1 → **Undo (Ctrl+Z)** | Supported |
| Button 2 → **Redo (Ctrl+Y)** | Supported |
| 100% active area mapping | Supported |
| Pure Python + `libusb` + `uinput` | Supported |

---

## Demo

![Hover + Pressure](screenshots/hover.jpg)  
*Hovering shows cursor. Pressure changes stroke weight in Infinite Painter.*

![Undo/Redo GIF](screenshots/undo_redo.gif)  
*Barrel buttons trigger Ctrl+Z / Ctrl+Y in any app.*

---

## Requirements

- **Rooted Android** (Magisk, KernelSU, etc.)
- **Termux** with `tsu` or `su`
- **USB OTG cable**
- **Wacom Intuos CTL-480** (or compatible)
- **Stylus-aware app** (Infinite Painter, Medibang, Sketchbook)

---

## Quick Start


# 1. Install Termux packages
pkg install python libusb git

# 2. Install Python deps
pip install pyusb

# 3. Clone & run
git clone https://github.com/yourname/wacom-android-userspace-driver
cd wacom-android-userspace-driver/src
tsu
python wacom_driver.py
Press Ctrl+C to stop.

Configuration
Edit src/wacom_driver.py:
SCREEN_WIDTH = 2048
SCREEN_HEIGHT = 1536

# Pressure curve (easier max pressure)
PRESSURE_EASING = 1.8
PRESSURE_OFFSET = 50
PRESSURE_CLAMP_MIN = 100

Tested On
Device
ROM
Kernel
Status
Samsung Galaxy Tab S2
LineageOS 21
3.10.108
Supported
Any rooted Android
Any
3.10+ with uinput
Supported

Troubleshooting
See TROUBLESHOOTING.md

License
MIT License — Free to use, modify, and distribute.

Credits
	•	Wacom HID report format: Linux hid-wacom driver
	•	uinput legacy API: Linux kernel docs
	•	You: @yourusername — for resurrecting old hardware

“Why spend $40 on a half-working stylus when you can run a real Wacom for free?”

---

## How to Use

1. **Copy everything above** (from `# Wacom Android Userspace Driver` to the last `---`)
2. **Paste into `README.md`** in your repo root
3. **Replace `yourname`** with your GitHub username
4. **Add images** to `screenshots/` folder

---


[![Stars](https://img.shields.io/github/stars/yourname/wacom-android-userspace-driver?style=social)](#)
[![Forks](https://img.shields.io/github/forks/yourname/wacom-android-userspace-driver?style=social)](#)


