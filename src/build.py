#!/usr/bin/env python3
"""index.html ve v.html'i tek dosya olarak üretir (engine + qrlib + app gömülü)."""
import pathlib
SRC = pathlib.Path(__file__).parent
ROOT = SRC.parent
eng = (SRC / "engine.js").read_text(encoding="utf-8")
qr = (SRC / "qrlib.js").read_text(encoding="utf-8")
app = (SRC / "app.js").read_text(encoding="utf-8")
idx = (SRC / "index.tpl.html").read_text(encoding="utf-8")
g = (SRC / "g.tpl.html").read_text(encoding="utf-8")
t = (SRC / "t.tpl.html").read_text(encoding="utf-8")
r = (SRC / "r.tpl.html").read_text(encoding="utf-8")
v = (SRC / "v.tpl.html").read_text(encoding="utf-8")
for name, tpl in (("index.html", idx), ("v.html", v), ("g.html", g), ("t.html", t), ("r.html", r)):
    out = tpl.replace("/*QRLIB*/", qr.strip()).replace("/*ENGINE*/", eng.strip()).replace("/*APP*/", app.strip())
    (ROOT / name).write_text(out, encoding="utf-8")
    print(name, len(out.encode("utf-8")), "bytes")
