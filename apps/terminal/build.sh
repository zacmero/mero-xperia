#!/usr/bin/env bash
# Run from any directory; needs Docker, Python 3, curl and ImageMagick on host.
set -euo pipefail
cd "$(dirname "$0")/../.."
umask 077
mkdir -p local/apks local/terminal build/terminal
apk=local/apks/Term.apk
expected=4cbf6adb273a6afa01f7d5f4ea97ac22b5a97ce1a34c000f2ef308a6383e8821
if [[ ! -f $apk ]]; then
    curl --fail --location --output "$apk" https://jackpal.github.io/Android-Terminal-Emulator/downloads/Term.apk
fi
printf '%s  %s\n' "$expected" "$apk" | sha256sum --check
docker build -t mero-xperia-terminal-tools apps/terminal
tool=(docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/work" mero-xperia-terminal-tools)
"${tool[@]}" apktool d -f -p /tmp/framework "$apk" -o build/terminal/decoded
python3 apps/terminal/customize.py build/terminal/decoded
"${tool[@]}" apktool b -p /tmp/framework build/terminal/decoded -o build/terminal/unsigned.apk
if [[ ! -f local/terminal/signing.jks ]]; then
    python3 -c 'import secrets; from pathlib import Path; Path("local/terminal/signing-password").write_text(secrets.token_urlsafe(32))'
    "${tool[@]}" keytool -genkeypair -noprompt -alias mero-terminal -keyalg RSA -keysize 2048 \
        -sigalg SHA1withRSA -validity 10000 -dname CN=MeroTerminal -storetype JKS \
        -keystore local/terminal/signing.jks -storepass:file local/terminal/signing-password \
        -keypass:file local/terminal/signing-password
fi
chmod 600 local/terminal/signing.jks local/terminal/signing-password
"${tool[@]}" zipalign -f 4 build/terminal/unsigned.apk build/terminal/aligned.apk
"${tool[@]}" apksigner sign --min-sdk-version 4 --v1-signing-enabled true --v2-signing-enabled false \
    --ks local/terminal/signing.jks --ks-key-alias mero-terminal \
    --ks-pass file:local/terminal/signing-password \
    --out build/terminal/MeroTerminal.apk build/terminal/aligned.apk
"${tool[@]}" apksigner verify --verbose --min-sdk-version 4 build/terminal/MeroTerminal.apk
echo 'Built build/terminal/MeroTerminal.apk (org.mero.xperia.terminal)'
