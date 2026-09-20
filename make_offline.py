#!/usr/bin/env python3
"""Regenerate offline.html from index.html + cards.json.

offline.html is index.html with the deck inlined as EMBEDDED_CARDS and the
cards.json fetch replaced, so it works from a file:// origin. Run this after
any renderer change or once a batch of cards is final:

    python3 make_offline.py
"""
import io, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
idx = io.open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
cards = json.load(io.open(os.path.join(HERE, "cards.json"), encoding="utf-8"))

BOOT = "/* ===================== Boot ===================== */"
if idx.count(BOOT) != 1:
    raise SystemExit("boot marker not found exactly once in index.html")

embed = (
    "/* ===================== Embedded deck (offline copy) ===================== */\n"
    "const EMBEDDED_CARDS = "
    + json.dumps(cards, ensure_ascii=False, indent=1)
    + ";\n\n"
)

out = idx.replace(BOOT, embed + BOOT)

# swap the fetch-based loader for the embedded one
loader = re.search(
    r"async function loadBuiltin\(\)\{.*?\n\}", out, re.S)
if not loader:
    raise SystemExit("loadBuiltin() not found")
out = out[:loader.start()] + "async function loadBuiltin(){ BUILTIN=EMBEDDED_CARDS; }" + out[loader.end():]

io.open(os.path.join(HERE, "offline.html"), "w", encoding="utf-8").write(out)
print("offline.html regenerated — %d cards, %.1f MB" % (len(cards), len(out) / 1e6))
