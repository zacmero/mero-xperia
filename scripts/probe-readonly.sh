#!/usr/bin/env bash
# Non-destructive inventory for the Xperia X10 mini pro. Never use this on
# an untrusted USB-connected host. Review logs before committing anything.
set -euo pipefail

if ! command -v adb >/dev/null 2>&1; then
  printf 'adb missing; on Arch: sudo pacman -S android-tools\n' >&2
  exit 1
fi

printf '%s\n' '== connected ADB devices =='
adb devices

printf '%s\n' '== running build and ABI (read-only) =='
for prop in ro.product.model ro.product.device ro.build.version.release ro.build.display.id ro.product.cpu.abi; do
  printf '%s: ' "$prop"
  adb shell getprop "$prop" | tr -d '\r'
done

printf '%s\n' '== kernel =='
adb shell uname -a

printf '%s\n' '== memory summary =='
adb shell cat /proc/meminfo | head -n 8

printf '%s\n' '== filesystem space =='
adb shell df

printf '%s\n' 'This prints local diagnostic information. Do NOT commit raw output if it contains identifiers.'
