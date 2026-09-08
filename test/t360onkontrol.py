#!/usr/bin/env python3
"""OBSKURA 360 v0.5 — SAHA KONTROLÜ (t.html) testi.
   Kontrol sayfası her şey yolundayken YEŞİL, bozuk kurulumda KIRMIZI vermeli.
   İki senaryo: (A) her şey çalışıyor, (B) preset reddediyor + FX yok + müzik ses katmanı kurulmuyor."""
import json, sys, time, threading, http.server, socketserver, pathlib, functools
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8368
TINY = pathlib.Path("/tmp/tiny.mp4").read_bytes()
BASE = f"http://localhost:{PORT}/"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Quiet, directory=str(ROOT))) as h:
        h.serve_forever()
threading.Thread(target=serve, daemon=True).start(); time.sleep(0.4)

S_OK = {"evt": "Ön Kontrol", "sure": 15, "cldName": "rqhgtbvd", "cldPreset": "booth_qr",
        "muzikler": [{"n": "t1", "pid": "booth360/_muzik/track1"}], "muzikSec": "booth360/_muzik/track1",
        "logoPid": "booth360/_logo/yopi", "fxHave": {"yildiz": 1, "kalp": 1, "konfeti": 1, "sparkle": 1},
        "turSn": 10, "yuzSn": 0, "paket": "efektli", "kadraj": "genis916", "krediTl": 21.31,
        "siteUrl": BASE}
MODE = {"upload_ok": True, "fx_ok": True, "audio_ok": True}

def route(r, req):
    u = req.url
    if "api.cloudinary.com" in u:
        if req.method == "HEAD":
            r.fulfill(status=200, headers={"access-control-allow-origin": "*"}, body=""); return
        if not MODE["upload_ok"]:
            r.fulfill(status=400, content_type="application/json",
                      body='{"error":{"message":"Upload preset must be whitelisted for unsigned uploads"}}'); return
        r.fulfill(status=200, content_type="application/json",
                  body=json.dumps({"public_id": "booth360/_deneme/t1", "version": 1725500000, "duration": 1.4})); return
    if "res.cloudinary.com" in u:
        if "/video/list/" in u:
            r.fulfill(status=200, content_type="application/json", headers={"access-control-allow-origin": "*"},
                      body=json.dumps({"resources": [{"public_id": "a", "version": 1, "format": "mp4"}]})); return
        if not MODE["fx_ok"] and "/_fx/" in u:
            r.fulfill(status=404, headers={"access-control-allow-origin": "*"}, body=""); return
        if not MODE["audio_ok"] and "l_audio:" in u:
            r.fulfill(status=400, headers={"access-control-allow-origin": "*", "x-cld-error": "bad audio"}, body=""); return
        if req.method == "HEAD":
            r.fulfill(status=200, headers={"access-control-allow-origin": "*", "content-type": "video/mp4",
                                           "accept-ranges": "bytes", "content-length": str(len(TINY))}, body=""); return
        r.fulfill(status=200, headers={"access-control-allow-origin": "*"}, content_type="video/mp4", body=TINY); return
    r.continue_()

res = []
def ok(n, c, extra=""):
    res.append((n, bool(c), extra)); print(("  ✔ " if c else "  ✘ ") + n + (("  — " + extra) if extra else ""))

def calistir(ctx, errs):
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "t.html"); pg.wait_for_selector("#run")
    pg.click("#run")
    pg.wait_for_selector("#sum:not([hidden])", timeout=180000)
    rows = pg.evaluate("""Array.from(document.querySelectorAll('#list .it')).map(function(d){
        return {ad:d.querySelector('.nm').textContent, dur:d.className.replace('it','').trim(),
                ds:d.querySelector('.ds').textContent}})""")
    ozet = pg.text_content("#sum")
    rapor = pg.evaluate("window.__rapor||''")
    pg.close()
    return rows, ozet, rapor

with sync_playwright() as p:
    br = p.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
                                 "--autoplay-policy=no-user-gesture-required"])

    # ---------- A) HER ŞEY YOLUNDA ----------
    ctx = br.new_context(viewport={"width": 430, "height": 932}, permissions=["camera"])
    ctx.add_init_script("try{localStorage.setItem('booth360.v1',JSON.stringify(" + json.dumps(S_OK) + "))}catch(e){}")
    ctx.route("**/*cloudinary.com/**", route)
    errs = []
    rows, ozet, rapor = calistir(ctx, errs)
    adlar = [r["ad"] for r in rows]
    hatalar = [r for r in rows if r["dur"] == "err"]
    ok("sağlam kurulum: hiç HATA yok", not hatalar, "; ".join(r["ad"] + ": " + r["ds"][:50] for r in hatalar)[:220])
    ok("özet 'hazır' diyor", "hazır" in ozet.lower(), ozet[:70])
    for gerekli in ["İnternet", "Ayarlar", "Kamera", "Buluta yükleme", "Efekt videoları (FX)", "Logo", "Müzik",
                    "Karekod sayfası (v.html)", "Etkinlik galerisi", "Telefon"]:
        ok("kontrol edildi: " + gerekli, any(gerekli in a for a in adlar))
    sab = [r for r in rows if "Yıldız" in r["ad"] or "Kalp" in r["ad"] or "Kulüp" in r["ad"]]
    ok("6 şablonun her biri tek tek denendi", len([r for r in rows if "·" not in r["ad"] and any(
        e in r["ad"] for e in ["✨", "💗", "🎉", "🎩", "⏪", "🪩"])]) == 6,
       "%d şablon satırı" % len([r for r in rows if any(e in r["ad"] for e in ["✨", "💗", "🎉", "🎩", "⏪", "🪩"])]))
    muz = next((r for r in rows if r["ad"] == "Müzik"), {})
    ok("müzik: ses katmanının videoya bindiği doğrulandı", muz.get("dur") == "ok" and "ses katmanı" in muz.get("ds", ""),
       muz.get("ds", "")[:80])
    ok("her şablon satırı TL maliyeti yazıyor", all("TL" in r["ds"] for r in sab), (sab[0]["ds"][:70] if sab else ""))
    ok("özet toplam TL maliyeti veriyor", "TL" in ozet, ozet[-70:])
    ok("kopyalanabilir rapor üretildi", "SAHA KONTROLÜ" in rapor and "OK  " in rapor, "%d karakter" % len(rapor))
    ok("kontrol sayfasında JS hatası yok", not errs, "; ".join(errs)[:160])
    ctx.close()

    # ---------- B) BOZUK KURULUM: preset kapalı + FX yok + ses katmanı kurulmuyor ----------
    MODE.update(upload_ok=False, fx_ok=False, audio_ok=False)
    ctx2 = br.new_context(viewport={"width": 430, "height": 932}, permissions=["camera"])
    ctx2.add_init_script("try{localStorage.setItem('booth360.v1',JSON.stringify(" + json.dumps(S_OK) + "))}catch(e){}")
    ctx2.route("**/*cloudinary.com/**", route)
    e2 = []
    rows2, ozet2, _ = calistir(ctx2, e2)
    def sat(ad): return next((r for r in rows2 if r["ad"] == ad), {})
    y = sat("Buluta yükleme")
    ok("bozuk preset yakalandı", y.get("dur") == "err" and "Unsigned" in y.get("ds", ""), y.get("ds", "")[:90])
    f = sat("Efekt videoları (FX)")
    ok("eksik FX videoları yakalandı", f.get("dur") == "err", f.get("ds", "")[:90])
    m = sat("Müzik")
    ok("ses katmanının kurulmadığı yakalandı", m.get("dur") == "err" and "SES KATMANI" in m.get("ds", ""), m.get("ds", "")[:90])
    ok("özet 'sahaya çıkma' uyarısı veriyor", "HATA" in ozet2 and "çıkma" in ozet2, ozet2[:70])
    ok("bozuk senaryoda da JS hatası yok", not e2, "; ".join(e2)[:160])
    ctx2.close()

    # ---------- C) AYAR BAĞLANTISIYLA AÇILIŞ: hafızası bos telefon tek linkle kurulur ----------
    MODE.update(upload_ok=True, fx_ok=True, audio_ok=True)
    import base64
    payload = dict(S_OK); payload["evt"] = "Ortak Denemesi"; payload["deneme"] = 1
    blob = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode()).decode().replace("+", "-").replace("/", "_")
    ctx3 = br.new_context(viewport={"width": 430, "height": 932}, permissions=["camera"])
    ctx3.route("**/*cloudinary.com/**", route)
    e3 = []
    p3 = ctx3.new_page()
    p3.on("pageerror", lambda e: e3.append(str(e)))
    p3.add_init_script("try{localStorage.removeItem('booth360.v1')}catch(e){}")
    p3.goto(BASE + "t.html#ayar=" + blob); p3.wait_for_selector("#run")
    ok("boş telefon: kontrol sayfası bağlantıdan ayarları yükledi",
       p3.evaluate("(JSON.parse(localStorage.getItem('booth360.v1')||'{}')).evt") == "Ortak Denemesi")
    ok("kontrol sayfası ayarın yüklendiğini yazıyor", "bağlantıdan yüklendi" in (p3.text_content("#sub") or ""))
    ok("bağlantıdaki ayar adres çubuğunda kalmıyor", "#ayar=" not in p3.evaluate("location.hash"))
    p3.click("#run"); p3.wait_for_selector("#sum:not([hidden])", timeout=180000)
    r3 = p3.evaluate("""Array.from(document.querySelectorAll('#list .it')).map(function(d){
        return {ad:d.querySelector('.nm').textContent, dur:d.className.replace('it','').trim()}})""")
    ok("bağlantıyla gelen kurulumda kontrol temiz geçti", not [x for x in r3 if x["dur"] == "err"],
       "; ".join(x["ad"] for x in r3 if x["dur"] == "err")[:120])
    ok("deneme modu uyarısı çıktı", any("DENEME" in x["ad"] for x in r3))
    ok("bağlantı açılışında JS hatası yok", not e3, "; ".join(e3)[:160])
    ctx3.close()
    br.close()

bad = [r for r in res if not r[1]]
print(f"\nSONUÇ: {len(res)-len(bad)}/{len(res)} geçti" + (" — HATALAR: " + ", ".join(r[0] for r in bad) if bad else ""))
sys.exit(1 if bad else 0)
