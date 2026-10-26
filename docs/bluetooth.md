# Bluetooth exploration — 2026-10-26

Device: U20a, Android 1.6, build 1.2.A.1.181. Private device addresses, discovered-device lists and diagnostic captures remain under ignored `captures/bluetooth-recovery-2026-10-26/`.

## Verified pairing

Bluetooth was initially off on the phone. The user enabled it and made it discoverable. The Linux adapter was powered on. Pairing used legacy PIN exchange, rather than modern numeric-comparison pairing.

The first attempt failed authentication after different PINs were entered. Subsequent host-initiated retries returned `ConnectionAttemptFailed`, even after rediscovery; the exact cause remains unconfirmed. Initiating pairing from the phone to the computer and using the same PIN at both ends succeeded. Linux reported **Paired: yes** and **Bonded: yes**. Permanent automatic trust was not enabled.

The host resolved these advertised phone services:

- OBEX Object Push (`0x1105`).
- Audio Source (`0x110a`).
- A/V Remote Control Target (`0x110c`).
- Headset Audio Gateway (`0x1112`).
- Handsfree Audio Gateway (`0x111f`).

An advertised service is not proof that a transfer or audio stream works. No serial-port service was advertised in this discovery. Bluetooth pairing alone does not provide a terminal or ADB shell.

## Paired versus connected

**Paired/bonded** means the peers store shared keys. **Connected** means a live transport or profile session exists. A phone can correctly report paired but not connected while idle. It is unnecessary to keep an audio connection open merely to preserve a bond. Automatic audio-service authorization prompts during this test were not accepted.

Host scanning and discoverability were disabled after pairing; the original host discoverability-timeout setting was restored. The phone's temporary discoverability is controlled by its UI timer.

## Firmware/API distinctions

The [manufacturer's March 2011 white paper](https://www-support-downloads.sonymobile.com/u20/whitepaper_EN_u20_x10_mini_pro.pdf) describes Bluetooth 2.0+EDR and profiles including Object Push, Serial Port and audio. It describes the later product software and does not establish every profile on this Android 1.6 handset; the services listed above were observed directly.

The [AOSP Android 1.6 BluetoothDevice source](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-1.6_r2/core/java/android/bluetooth/BluetoothDevice.java) marks its Bluetooth API hidden and warns that it is not finalized. A custom Bluetooth app must account for this old API surface instead of assuming modern Android examples compile and run unchanged.

## File-transfer test

OBEX file transfer is a separate experiment from pairing. When the card was exported over USB mass storage it was not mounted on the phone. The host card mount was safely unmounted and the user disabled USB storage sharing before attempting a Bluetooth receive. This avoids trying to save to unavailable phone-side storage.

**Results:** The OBEX session connected successfully. A generated 73-byte `.txt` file was rejected twice with `Forbidden`. A generated 313-byte PNG then prompted the user for acceptance and completed successfully. This comparison suggests a file-type/receive-policy restriction; it does not establish a complete supported MIME-type list.

The received PNG was found at `/sdcard/Bluetooth/mero-bluetooth-test-20261026.png`. It was pulled back through ADB solely for verification and matched the original **byte for byte**. SHA-256: `5e2b74cb81c842b1d4e1fa31b053599d5e19d68100fbbb123dd53a0ce2d52f55`. The file was sent over Bluetooth, not pushed to the phone with ADB.

The host's `bluez-obex` package was absent, but an existing user-owned OBEX compatibility daemon was already running. Matching Arch `bluez-obex` 5.87-2 and libical 4.0.7-1 archives were extracted under ignored `local/tools/obex/`; their signatures verified against the host Arch keyring. The local `obexctl` client used the existing daemon. An attempted second daemon exited with `Name already in use` and was not left running. No system package installation or replacement of the existing daemon was performed.

The test OBEX session was disconnected afterward. Pairing remains stored; host discoverability/scanning are off. The SD card remains mounted on the phone after the user disabled USB storage sharing. Private verification metadata: `captures/bluetooth-recovery-2026-10-26/png-transfer-verification.json`.
