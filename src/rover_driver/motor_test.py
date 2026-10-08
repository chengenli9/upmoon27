#!/usr/bin/env python3
"""
Standalone drive-motor bench test for the UPR/upmoon rover.
No ROS, no repo, no Docker needed. Just:  pip install pysabertooth pyserial

Matches the parameters in src/frontend/frontend/drive_motors.py:
  - two Sabertooth controllers, 9600 baud, address 128
  - left side on one ACM port, right side on the other
  - "forward" on a side = drive(1, +s) and drive(2, -s)  (motors mounted mirrored)

!!! SAFETY: put the rover ON BLOCKS so all wheels are off the ground before running.
    Keep the e-stop / battery disconnect in hand. Start at low speed.

Usage:
  python3 motor_test.py --list                 # just list serial ports, do nothing
  python3 motor_test.py                         # auto-pick the two ACM ports
  python3 motor_test.py --left /dev/ttyACM0 --right /dev/ttyACM1
  python3 motor_test.py --speed 15 --dwell 1.5  # gentler / shorter pulses
"""

import argparse
import sys
import time

from serial.tools import list_ports

try:
    from pysabertooth import Sabertooth
except ImportError:
    sys.exit("pysabertooth not installed.  Run:  pip install pysabertooth pyserial")

ARDUINO_VID, ARDUINO_PID = 0x2341, 0x0043  # exclude the Arduino, same as the real driver


def list_serial_ports():
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return ports
    print("Serial ports:")
    for p in ports:
        tag = "  <-- Arduino (skip for motors)" if (p.vid == ARDUINO_VID and p.pid == ARDUINO_PID) else ""
        print(f"  {p.device:15}  {p.description}  [vid={p.vid} pid={p.pid}]{tag}")
    return ports


def auto_ports():
    """Return up to two ACM ports that are NOT the Arduino, lowest device name first."""
    acm = []
    for p in list_ports.comports():
        if p.vid == ARDUINO_VID and p.pid == ARDUINO_PID:
            continue
        if p.device.startswith("/dev/ttyACM"):
            acm.append(p.device)
    return sorted(acm)[:2]


def connect(port, name):
    try:
        s = Sabertooth(port, baudrate=9600, address=128, timeout=0.1)
        print(f"[{name}] connected on {port}")
        return s
    except Exception as e:
        print(f"[{name}] FAILED to connect on {port}: {e}")
        return None


def pulse(saber, name, motor, speed, dwell):
    """Spin one motor at `speed` for `dwell` seconds, then stop it."""
    if saber is None:
        print(f"[{name}] (no connection, skipping motor {motor})")
        return
    print(f"[{name}] motor {motor}  ->  speed {speed:+d}  for {dwell}s")
    saber.drive(motor, speed)
    time.sleep(dwell)
    saber.drive(motor, 0)
    time.sleep(0.3)


def side_forward(saber, name, speed, dwell):
    """Drive a whole side 'forward' using the mirrored-motor convention from the real driver."""
    if saber is None:
        print(f"[{name}] (no connection, skipping side)")
        return
    print(f"[{name}] BOTH motors forward (1:{speed:+d}, 2:{-speed:+d}) for {dwell}s")
    saber.drive(1, speed)
    saber.drive(2, -speed)
    time.sleep(dwell)
    saber.stop()
    time.sleep(0.3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="list serial ports and exit")
    ap.add_argument("--left", help="left Sabertooth port (default: auto)")
    ap.add_argument("--right", help="right Sabertooth port (default: auto)")
    ap.add_argument("--speed", type=int, default=20, help="test speed 1-100 (default 20)")
    ap.add_argument("--dwell", type=float, default=2.0, help="seconds per pulse (default 2)")
    args = ap.parse_args()

    list_serial_ports()
    if args.list:
        return

    left_port, right_port = args.left, args.right
    if not (left_port and right_port):
        found = auto_ports()
        if len(found) < 2:
            sys.exit(f"\nNeed two Sabertooth ACM ports, found {found}. "
                     f"Pass them explicitly with --left/--right.")
        left_port = left_port or found[0]
        right_port = right_port or found[1]
    print(f"\nUsing  left={left_port}  right={right_port}\n")

    saber_l = connect(left_port, "Left")
    saber_r = connect(right_port, "Right")
    if saber_l is None and saber_r is None:
        sys.exit("Neither controller connected — check power, USB, and Sabertooth DIP mode.")

    input("Wheels OFF THE GROUND? e-stop ready? Press Enter to start (Ctrl-C aborts)... ")

    try:
        print("\n== Each motor individually (isolates a dead wheel/driver) ==")
        pulse(saber_l, "Left",  1, args.speed, args.dwell)
        pulse(saber_l, "Left",  2, args.speed, args.dwell)
        pulse(saber_r, "Right", 1, args.speed, args.dwell)
        pulse(saber_r, "Right", 2, args.speed, args.dwell)

        print("\n== Each side forward together ==")
        side_forward(saber_l, "Left",  args.speed, args.dwell)
        side_forward(saber_r, "Right", args.speed, args.dwell)

        print("\nDone.")
    except KeyboardInterrupt:
        print("\nAborted.")
    finally:
        for s, n in ((saber_l, "Left"), (saber_r, "Right")):
            if s is not None:
                try:
                    s.stop()
                    print(f"[{n}] stopped")
                except Exception:
                    pass


if __name__ == "__main__":
    main()