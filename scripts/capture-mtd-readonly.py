#!/usr/bin/env python3
"""Copy exposed MTD partitions through a temporary root shell without writing flash.

The phone's old ADB daemon cannot stream binary data with ``exec-out``. Each
read-only MTD character-device read is staged in its 4 MiB tmpfs, pulled to
the host, checked for the exact expected length, and appended to a private
file. This captures the main-area bytes only, not NAND OOB/ECC metadata.
"""

import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys


HELPER = "/sqlite_stmt_journals/mero-temp-root-20261026/root-helper"
REMOTE_CHUNK = "/sqlite_stmt_journals/mero-temp-root-20261026/chunk"
BLOCK = 131072
BLOCKS_PER_CHUNK = 16
CHUNK = BLOCK * BLOCKS_PER_CHUNK


def run(*args):
    result = subprocess.run(["rtk", *args], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{' '.join(args)}: {result.stderr or result.stdout}")
    return result.stdout + result.stderr


def root(command):
    # Old adb shell joins argv into a remote command. The inner quotes keep
    # the entire shell program in one -c argument to the setuid helper.
    return run("adb", "shell", HELPER, "-c", f'"{command}"')


def partitions():
    lines = run("adb", "shell", "cat", "/proc/mtd").splitlines()
    found = []
    for line in lines:
        match = re.fullmatch(r'mtd(\d+):\s+([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+"([a-zA-Z0-9_-]+)"', line.strip())
        if match:
            number, size, name = match.groups()
            found.append((int(number), int(size, 16), name))
    if [(number, name) for number, _, name in found] != [
        (0, "system"), (1, "cache"), (2, "appslog"), (3, "userdata")
    ]:
        raise RuntimeError(f"unexpected MTD layout: {found}")
    return found


def capture(number, size, name, destination):
    final = destination / f"mtd{number}-{name}.img"
    partial = destination / f"mtd{number}-{name}.img.partial"
    temp = destination / ".adb-chunk"
    if final.exists():
        if final.stat().st_size != size:
            raise RuntimeError(f"wrong size in existing {final}")
        print(f"{final.name}: already complete", flush=True)
        return
    completed = partial.stat().st_size if partial.exists() else 0
    if completed % CHUNK:
        raise RuntimeError(f"partial file ends mid-chunk: {partial}")
    if completed > size:
        raise RuntimeError(f"partial file exceeds partition: {partial}")
    if size % BLOCK:
        raise RuntimeError(f"partition size is not block-aligned: {name}")
    if partial.exists():
        print(f"{final.name}: resuming at {completed}/{size}", flush=True)
    with partial.open("ab") as output:
        os.chmod(partial, 0o600)
        for offset in range(completed, size, CHUNK):
            expected = min(CHUNK, size - offset)
            blocks = expected // BLOCK
            source = f"/dev/mtd/mtd{number}ro"
            remote = f"dd if={source} of={REMOTE_CHUNK} bs={BLOCK} skip={offset // BLOCK} count={blocks} && chmod 644 {REMOTE_CHUNK}"
            summary = root(remote)
            if f"{expected} bytes transferred" not in summary:
                raise RuntimeError(f"MTD read failed at {name}+{offset}: {summary}")
            run("adb", "pull", REMOTE_CHUNK, str(temp))
            if temp.stat().st_size != expected:
                raise RuntimeError(f"ADB pull size mismatch at {name}+{offset}")
            with temp.open("rb") as source_file:
                while data := source_file.read(1024 * 1024):
                    output.write(data)
            temp.unlink()
            if ((offset + expected) // CHUNK) % 8 == 0 or offset + expected == size:
                print(f"{final.name}: {offset + expected}/{size} bytes", flush=True)
        output.flush()
        os.fsync(output.fileno())
    if partial.stat().st_size != size:
        raise RuntimeError(f"capture size mismatch: {partial}")
    partial.replace(final)
    digest = hashlib.sha256()
    with final.open("rb") as image:
        while data := image.read(4 * 1024 * 1024):
            digest.update(data)
    print(f"SHA256 {digest.hexdigest()}  {final.name}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--only", nargs="*", choices=["system", "cache", "appslog", "userdata"])
    args = parser.parse_args()
    args.destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(args.destination, 0o700)
    if "/sbin/hotplug" not in run("adb", "shell", "cat", "/proc/sys/kernel/hotplug").splitlines():
        raise RuntimeError("stock hotplug was not restored")
    if "uid=0(root)" not in root("id"):
        raise RuntimeError("temporary root shell is unavailable")
    root("sync")
    try:
        for number, size, name in partitions():
            if args.only and name not in args.only:
                continue
            capture(number, size, name, args.destination)
    finally:
        # This Android 1.6 toolbox rm does not support -f.
        run("adb", "shell", "rm", REMOTE_CHUNK)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError) as error:
        print(f"capture failed: {error}", file=sys.stderr)
        sys.exit(1)
