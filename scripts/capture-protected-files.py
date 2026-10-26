#!/usr/bin/env python3
"""Copy selected root-only Android files through 2 MiB RAM staging chunks.

Input is a private UTF-8 file with one absolute /data/... path per line.
This deliberately makes a file copy, not a consistent snapshot of live apps.
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
CHUNK = 16 * BLOCK


def adb(*args):
    result = subprocess.run(["rtk", "adb", *args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout + result.stderr


def root(command):
    return adb("shell", HELPER, "-c", f'"{command}"')


def read_size(source):
    listing = root(f"ls -l {source}").strip().splitlines()
    if len(listing) != 1:
        raise RuntimeError(f"cannot identify {source}: {listing}")
    fields = listing[0].split()
    if len(fields) < 4 or not fields[0].startswith("-"):
        raise RuntimeError(f"not a regular file: {source}: {listing[0]}")
    return int(fields[3])


def copy_file(source, destination):
    size = read_size(source)
    output = destination / source.lstrip("/")
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temp = output.with_name(output.name + ".partial")
    pull = destination / ".adb-chunk"
    digest = hashlib.sha256()
    with temp.open("wb") as target:
        os.chmod(temp, 0o600)
        for offset in range(0, size, CHUNK):
            expected = min(CHUNK, size - offset)
            summary = root(
                f"dd if={source} of={REMOTE_CHUNK} bs={BLOCK} "
                f"skip={offset // BLOCK} count=16 && chmod 644 {REMOTE_CHUNK}"
            )
            if f"{expected} bytes transferred" not in summary:
                raise RuntimeError(f"read failed at {source}+{offset}: {summary}")
            adb("pull", REMOTE_CHUNK, str(pull))
            if pull.stat().st_size != expected:
                raise RuntimeError(f"ADB size mismatch at {source}+{offset}")
            with pull.open("rb") as staged:
                while data := staged.read(1024 * 1024):
                    target.write(data)
                    digest.update(data)
            pull.unlink()
        target.flush()
        os.fsync(target.fileno())
    if temp.stat().st_size != size:
        raise RuntimeError(f"file size mismatch: {source}")
    temp.replace(output)
    print(f"{digest.hexdigest()}  {source}  {size}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths_file", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    sources = [line.strip() for line in args.paths_file.read_text().splitlines() if line.strip()]
    if len(sources) != len(set(sources)):
        raise RuntimeError("duplicate source path")
    for source in sources:
        if not re.fullmatch(r"/data/[A-Za-z0-9_./-]+", source) or ".." in Path(source).parts:
            raise RuntimeError(f"unsafe source path: {source}")
    if "/sbin/hotplug" not in adb("shell", "cat", "/proc/sys/kernel/hotplug").splitlines():
        raise RuntimeError("stock hotplug was not restored")
    if "uid=0(root)" not in root("id"):
        raise RuntimeError("temporary root shell is unavailable")
    args.destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(args.destination, 0o700)
    try:
        for source in sources:
            copy_file(source, args.destination)
    finally:
        adb("shell", "rm", REMOTE_CHUNK)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        print(f"capture failed: {error}", file=sys.stderr)
        sys.exit(1)
