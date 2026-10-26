# First ARMv6 program — verified on U20a

On 2026-10-26, `hello.c` compiled to a **1,048-byte** executable, ran on the stock Android 1.6 handset, printed its greeting and returned status 0. No root was needed. Source files live here; generated files remain ignored under `build/`.

## What it teaches

This is a freestanding C program. Instead of `main` and libc, the ELF entry point is `_start`. ARM EABI syscall registers select Linux `write` (4) and `exit` (1); `svc 0` enters the kernel. The exit status is 0 only if the complete greeting was written.

It deliberately avoids a dependency on Android's old Bionic library. This proves native ARMv6 execution, **not** compatibility of a modern Android NDK, ordinary libc-based C application, or Android APK.

## Build on this host

Verified tools: Clang 22.1.8 and the existing stable Rust toolchain's bundled LLD. No extra compiler package was installed. The linker path below is specific to this host's Rust installation.

```bash
rtk mkdir -p build/hello-native
rtk clang --target=arm-linux-gnueabi -march=armv6 -marm -mfloat-abi=soft -ffreestanding -fno-stack-protector -fno-pic -fno-pie -O2 -Wall -Wextra -Werror -c experiments/hello-native/hello.c -o build/hello-native/hello.o
rtk proxy "$HOME/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/rust-lld" -flavor gnu -m armelf_linux_eabi -static --entry=_start --build-id=none build/hello-native/hello.o -o build/hello-native/hello-xperia
rtk file build/hello-native/hello-xperia
rtk readelf -h build/hello-native/hello-xperia
```

Inspection reported 32-bit little-endian ARM, executable ELF, EABI5, soft-float, statically linked. Execution confirms this kernel accepts that output even though the stock inspected executables use EABI4.

## Transfer and execute

These commands write only the named experiment directory. If repeating this session, the directory already exists: skip `mkdir`, and expect `adb push` to replace this experiment's executable.

```bash
rtk adb shell mkdir /data/local/tmp/mero-xperia-hello-20261026
rtk adb push build/hello-native/hello-xperia /data/local/tmp/mero-xperia-hello-20261026/hello-xperia
rtk adb shell chmod 755 /data/local/tmp/mero-xperia-hello-20261026
rtk adb shell chmod 755 /data/local/tmp/mero-xperia-hello-20261026/hello-xperia
rtk adb shell '/data/local/tmp/mero-xperia-hello-20261026/hello-xperia; echo PROGRAM_EXIT=$?'
```

Verified output:

```text
Hello from the Xperia ARMv6!
PROGRAM_EXIT=0
```

The explicit marker captures the phone-side exit status; a successful host ADB invocation alone is insufficient evidence on this old daemon. Private output: `captures/experiment-2026-10-26/hello-result.txt`.

## Run directly on the phone

Open **Mero Terminal** and type the following there (without RTK, which is a host-only tool):

```sh
cd /data/local/tmp/mero-xperia-hello-20261026
./hello-xperia
echo $?
```

Expect the greeting followed by `0`. The program is already installed; compiling again or connecting USB is unnecessary just to run it. It is a shell executable, so it has no launcher icon of its own.

The experiment directory and executable now have mode `755`: other app users can traverse/read/execute this experiment, but only its owner can modify it. Previously mode `700` restricted execution to ADB's shell UID. No parent or protected system-directory permissions were changed. After this permission update the binary was re-run through ADB with the expected greeting and exit 0; the user can now try the local-terminal commands above.
