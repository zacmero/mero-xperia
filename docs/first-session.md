# First safe hands-on session

Goal: **preserve personal data and identify the actual running environment**. No rooting, flashing, factory reset, account login, or network-facing experimentation yet.

## 0 — Physical and preservation checks

- [ ] Examine the battery for swelling, leaks, punctures, abnormal heat, or unusual odor. Stop using it if any are present.
- [ ] Inspect the micro-USB socket and cable for damage; avoid forcing connectors.
- [ ] Verify the phone still starts and note current behavior, settings, battery indicator, keyboard response.
- [ ] Check for a microSD card. If it contains important files, **make a separate verified copy before experiments**.
- [ ] Avoid logging into primary accounts or connecting this obsolete Android 1.6 device to the public Internet.
- [ ] Keep SIM cards and personal data out of public photos/docs.

## 1 — Prepare Arch Linux host

**Connection result (2026-10-25):** Replacing the cable made the phone's USB notification appear. The user selected **Mount** and could see a folder on the host; USB debugging was enabled. Linux independently detected `0fce:2138` as `Xperia X10 mini pro (Debug)`. At that point ADB was not installed. On 2026-10-26 standalone ADB and non-root shell access were verified; see the [backup session](backup-session.md).

For this handset, check the notification bar after connecting a data cable and choose **Mount** to share the microSD as USB mass storage. The settings option **Unmount SD card** is not needed to initiate this connection. Storage sharing and ADB shell access are separate; mounting the card is not an ADB prerequisite.

If the phone only charges, first check `rtk lsusb`: if there is no phone entry, test another known data cable and a direct host port before troubleshooting mounting or ADB permissions.

```bash
sudo pacman -S android-tools
adb version
```

On the phone, navigate approximately to **Settings → Applications → Development → USB debugging** (Android 1.6-era UI may vary). Turn it off again when the session is over.

Use a **USB data cable** (not a charge-only cable). Verify the host sees the device:

```bash
adb devices
lsusb
```

If `adb devices` is empty: check the phone's USB mode, debugging setting and cable before assuming a driver or firmware problem. Linux udev access can also affect detection. If it says `offline`, capture the status and investigate the old daemon/host compatibility; do not immediately reset the phone.

**Security difference:** early Android builds lack modern per-host USB-debugging authorization. Treat any computer attached while debugging is on as trusted.

## 2 — Non-destructive commands

Run one at a time, inspect first:

```bash
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.display.id
adb shell getprop ro.product.cpu.abi
adb shell cat /proc/version
adb shell cat /proc/meminfo
adb shell df
adb shell mount
```

These are for collecting observations and **do not require root**. Some commands or paths may be missing on Android 1.6; report errors instead of applying invasive fixes.

Optional helper: `bash scripts/probe-readonly.sh`.

**Privacy:** even innocent-looking commands or `getprop` output can contain identifying information. Capture detailed raw results in a locally ignored directory, review/redact, and commit only selected non-identifying observations. Do not publish `getprop` wholesale, /proc/cpuinfo wholesale, logcat, or system dumps by default.

## 3 — Preserve microSD before modifying anything

If the phone can expose the microSD card as USB mass storage, or you have a USB card reader, copy its original contents into a **private local archive**. A full read-only disk image is an option when needed; if using one, be absolutely certain of the device path and never write to the original card.

For ordinary mounted-file backup, copy the files to a different disk and inspect results. Check a sample of photos/videos on the computer and create hashes for preservation. Do not store personal archives in the public repo.

The phone's internal app/data partitions are a separate backup challenge and **are not automatically included** when copying its microSD.

## 4 — Follow-up classification

Once ADB works, record:

- OS release, build, ABI, kernel; command availability.
- Total RAM (`MemTotal`) and free/used storage.
- SD card presence and whether its contents are already preserved.
- Hardware input (physical keyboard), touchscreen, Wi-Fi, Bluetooth, camera status.
- Status of unusual **Baseband version: Unknown** indicator — diagnosis pending, not necessarily a hardware defect.

Keep original software until restore paths are well understood.

### If anything goes wrong

Stop after diagnostics and record exactly what appeared on screen and in the terminal. Do not jump to fastboot/unlock/flash tools without a verified recovery plan for this **U20a** revision.
