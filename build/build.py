#!/usr/bin/env python3
"""Rebuild ../index.html from the live Google Sheet.

Two steps:
  1. build_seed.py  -> fetches the sheet, derives the ship model + attribute
                       catalog, and writes appdata.json (the embedded snapshot).
  2. this script    -> injects appdata.json + today's date into template.html
                       and writes ../index.html.

Usage:
    cd build
    python3 build_seed.py     # refresh appdata.json from the sheet
    python3 build.py          # produce ../index.html

You only need to rebuild when you change the HTML/JS in template.html or want to
refresh the embedded fallback snapshot. Visitors always get live data anyway: the
page re-fetches the sheet and caches it in the browser for 24h.
"""
import datetime, pathlib, sys

here = pathlib.Path(__file__).resolve().parent
tpl = (here / "template.html").read_text(encoding="utf-8")
data_path = here / "appdata.json"
if not data_path.exists():
    sys.exit("appdata.json not found - run `python3 build_seed.py` first.")

data = data_path.read_text(encoding="utf-8")
today = datetime.date.today().isoformat()
html = tpl.replace("__APPDATA__", data).replace("__BUILD_DATE__", today)

out = here.parent / "index.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html):,} bytes, build date {today})")
