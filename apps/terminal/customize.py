"""Apply the Mero terminal overlay to an apktool-decoded upstream release."""
from pathlib import Path
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1])
android = "{http://schemas.android.com/apk/res/android}"
ET.register_namespace("android", android[1:-1])
original = "jackpal.androidterm"
package = "org.mero.xperia.terminal"
manifest = root / "AndroidManifest.xml"
tree = ET.parse(manifest)
assert tree.getroot().get("package") == original
tree.getroot().set("package", package)
tree.getroot().set(android + "versionName", "1.0.70-mero1")
for node in tree.iter():
    if node.tag in {"activity", "activity-alias", "service", "receiver", "provider"}:
        for attr in ("name", "targetActivity"):
            name = node.get(android + attr)
            if name and (name.startswith(".") or "." not in name):
                node.set(android + attr, original + ("" if name.startswith(".") else ".") + name)
    for attr in ("name", "permission"):
        value = node.get(android + attr, "")
        if value.startswith(original + ".") and node.tag in {"action", "permission", "uses-permission"}:
            node.set(android + attr, package + value[len(original):])
        elif attr == "permission" and value.startswith(original + "."):
            node.set(android + attr, package + value[len(original):])
tree.write(manifest, encoding="utf-8", xml_declaration=True)

for path in (root / "res").glob("values*/*.xml"):
    text = path.read_text()
    for name, value in (("pref_fontsize_default", "20"), ("application_terminal", "Mero Terminal")):
        text = re.sub(r'(<string\b[^>]*\bname="' + name + r'"[^>]*>).*?(</string>)',
                      lambda m: m[1] + value + m[2], text, flags=re.S)
    path.write_text(text)

# Keep Java class names/JNI descriptors intact; isolate only app IDs and action keys.
literal = re.compile(r'"jackpal\.androidterm\.((?:permission|private|action|broadcast)\.[^"\n]+|[A-Z_]+|window_id)"')
for path in root.glob("smali*/**/*.smali"):
    text = path.read_text()
    text = literal.sub(lambda m: '"' + package + "." + m[1] + '"', text)
    text = text.replace('"' + original + '"', '"' + package + '"')
    path.write_text(text)

icon = Path(__file__).with_name("icon.svg")
icons = list((root / "res").glob("drawable*/ic_launcher.png"))
assert icons, "Upstream launcher icon not found"
for path in icons:
    width, height = struct.unpack(">II", path.read_bytes()[16:24])
    subprocess.run(["magick", str(icon), "-resize", f"{width}x{height}!", str(path)], check=True)
print(f"Customized {package}: 20-point font and {len(icons)} launcher icon densities")
