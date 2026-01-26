# Quarkn

Simple **Linux only** CLI notification tool.

Quarkn is a lightweight command-line utility for scheduling one-time notifications,
optionally executing commands or playing sounds after a specified delay.

This project started as a personal tool to solve a recurring workflow problem
and was later published as an open-source project.

---

## Status

Early development release (v0.x).

The interface and internal behavior may change as the project evolves.

---

## Features

- Timed notifications
- Repeated notifications
- Spam mode
- Interactive mode
- Optional sound playback
- Command execution after timer
- Fractional time support (e.g. `1.5h`, `2,5m`)
- No background services or daemons required

---

## Requirements

- Linux
- python3
- `notify-send`
- One of the following (optional, for sound playback):
  - `mpv`
  - `ffplay`
  - `vlc`

---

## Example

```bash
python3 quarkn.py -t 10mins -m "Take a break"
