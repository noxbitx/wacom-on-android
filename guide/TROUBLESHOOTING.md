
---

## `docs/TROUBLESHOOTING.md`

```md
# Troubleshooting

| Issue | Fix |
|------|-----|
| `Permission denied: /dev/uinput` | Run with `tsu` or `su -c` |
| `No such device` | Plug in tablet, check `lsusb` |
| No hover | App must support stylus (try Infinite Painter) |
| Pressure too hard | Lower `PRESSURE_EASING` to `1.5` |
| Cursor offset | Recalibrate `SCREEN_WIDTH/HEIGHT` with `wm size` |
