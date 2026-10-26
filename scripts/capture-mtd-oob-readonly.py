#!/usr/bin/env python3
"""Capture U20a NAND spare/OOB bytes through read-only MTD ioctls.

The companion on-phone ARM helper is built from experiments/temporary-root/
oob-capture.c and writes at most 2 MiB to tmpfs per invocation. This host
script pulls each chunk and verifies its exact byte count before appending.
"""

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys


ROOT = "/sqlite_stmt_journals/mero-temp-root-20261026/root-helper"
CAPTURE = "/sqlite_stmt_journals/mero-temp-root-20261026/oob-capture"
REMOTE = "/sqlite_stmt_journals/mero-temp-root-20261026/oob-chunk"
PAGE = 2048
OOB = 64
PAGES_PER_CHUNK = 32768
PARTITIONS = [
    (0, "system", 216006656),
    (1, "cache", 52428800),
    (2, "appslog", 262144),
    (3, "userdata", 222035968),
]


def adb(*args):
    result = subprocess.run(["rtk", "adb", *args], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout + result.stderr


def root(command):
    return adb("shell", ROOT, "-c", f'"{command}"')


def capture(index, name, size, destination):
    if size % PAGE:
        raise RuntimeError(f"invalid partition size: {name}")
    pages = size // PAGE
    total = pages * OOB
    final = destination / f"mtd{index}-{name}.oob"
    partial = destination / f"mtd{index}-{name}.oob.partial"
    pull = destination / ".adb-oob-chunk"
    if final.exists():
        if final.stat().st_size != total:
            raise RuntimeError(f"wrong size in existing {final}")
        print(f"{final.name}: already complete", flush=True)
        return
    completed = partial.stat().st_size if partial.exists() else 0
    if completed % (PAGES_PER_CHUNK * OOB) or completed > total:
        raise RuntimeError(f"invalid partial file length: {partial}")
    with partial.open("ab") as output:
        os.chmod(partial, 0o600)
        for first in range(completed // OOB, pages, PAGES_PER_CHUNK):
            count = min(PAGES_PER_CHUNK, pages - first)
            expected = count * OOB
            report = root(f"{CAPTURE} {index} {first} {count}")
            if f"pages={count} bytes={expected}" not in report:
                raise RuntimeError(f"OOB read failed at {name} page {first}: {report}")
            adb("pull", REMOTE, str(pull))
            if pull.stat().st_size != expected:
                raise RuntimeError(f"ADB size mismatch at {name} page {first}")
            with pull.open("rb") as staged:
                while data := staged.read(1024 * 1024):
                    output.write(data)
            pull.unlink()
            print(f"{final.name}: {(first + count) * OOB}/{total} bytes", flush=True)
        output.flush()
        os.fsync(output.fileno())
    if partial.stat().st_size != total:
        raise RuntimeError(f"OOB capture length mismatch: {final}")
    partial.replace(final)
    with final.open("rb") as image:
        digest = hashlib.file_digest(image, "sha256").hexdigest()
    print(f"SHA256 {digest}  {final.name}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(args.destination, 0o700)
    if "/sbin/hotplug" not in adb("shell", "cat", "/proc/sys/kernel/hotplug").splitlines():
        raise RuntimeError("stock hotplug was not restored")
    if "uid=0(root)" not in root("id"):
        raise RuntimeError("temporary root shell is unavailable")
    try:
        for index, name, size in PARTITIONS:
            capture(index, name, size, args.destination)
    finally:
        adb("shell", "rm", REMOTE)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError) as error:
        print(f"capture failed: {error}", file=sys.stderr)
        sys.exit(1)
