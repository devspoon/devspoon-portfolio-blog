"""Build static/vendor/bootstrap-icons-1.13.1/icons.svg with only the icons the project uses.

Usage: python tools/build_icon_sprite.py
Icons are found in templates as {% icon "name" %} and in JS as data-icon="name" / icon("name").
Fails if a referenced icon does not exist in the upstream sprite.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "tools" / "bootstrap-icons-1.13.1.svg"
OUT = ROOT / "static" / "vendor" / "bootstrap-icons-1.13.1" / "icons.svg"
PATTERNS = [r'\{%\s*icon\s+"([a-z0-9-]+)"', r'data-icon="([a-z0-9-]+)"', r'icon\("([a-z0-9-]+)"\)']


def used_icons():
    names = set()
    files = list((ROOT / "templates").rglob("*.html")) + list((ROOT / "static" / "js").rglob("*.js"))
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat in PATTERNS:
            names.update(re.findall(pat, text))
    return names


def main():
    upstream = UPSTREAM.read_text(encoding="utf-8")
    symbols = {m[2]: m[1] for m in re.finditer(r'(<symbol [^>]*\bid="([a-z0-9-]+)".*?</symbol>)', upstream, flags=re.S)}
    names = sorted(used_icons())
    missing = [n for n in names if n not in symbols]
    if missing:
        sys.exit(f"unknown icons: {missing}")
    body = "".join(symbols[n] for n in names)
    OUT.write_text('<svg xmlns="http://www.w3.org/2000/svg">' + body + "</svg>\n", encoding="utf-8")
    print(f"{len(names)} icons -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
