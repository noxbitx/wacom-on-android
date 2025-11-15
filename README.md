# Wacom Android Userspace Driver  
### *Turn any rooted Android tablet into a full Wacom Intuos*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Android 14 Tested](https://img.shields.io/badge/Android-14%20Tested-green)](#)

> **No kernel modules. No recompilation. Full hover, pressure, and undo/redo.**  
> Works on **Samsung Galaxy Tab S2 (LineageOS 21)** — and any rooted Android with `/dev/uinput`.

---

## Features

| Feature | Status |
|-------|--------|
| Hover cursor | Supported |
| 2048-level pressure | Supported (tunable) |
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

```bash
# 1. Install Termux packages
pkg install python libusb git

# 2. Install Python deps
pip install pyusb

# 3. Clone & run
git clone https://github.com/yourname/wacom-android-userspace-driver
cd wacom-android-userspace-driver/src
tsu
python wacom_driver.py
