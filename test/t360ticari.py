#!/usr/bin/env python3
"""OBSKURA 360 v0.5 — TİCARİ + KURTARMA testi.
   Doğruladığı şeyler: bulut maliyeti TL hesabı (aynı adres iki kez ücretlenmiyor),
   deneme modunun sayacı/galeriyi kirletmemesi, panel şifresinin değişebilmesi,
   ayar yedeği (metin + yer imi bağlantısı) ve hafıza silinince bağlantıdan geri gelmesi."""
import json, sys, time, threading, http.server, socketserver, pathlib, functools
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8366
TINY = pathlib.Path("/tmp/tiny.mp4").read_bytes()
BASE = f"http://localhost:{PORT}/"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Quiet, directory=str(ROOT))) as h:
        h.serve_forever()
threading.Thread(target=serve, daemon=True).start(); time.sleep(0.4)

INIT = {"evt": "Ticari Test", "sure": 3, "cldName": "rqhgtbvd", "cldPreset": "booth_qr",
        "muzikler": [], "muzikSec": "", "logoPid": "", "fxHave": {"yildiz": 1, "kalp": 1, "konfeti": 1, "sparkle": 1},
        "turSn": 10, "yuzSn": 0, "otoDon": 0, "paket": "efektli", "mod": "editli", "sayac": {}, "warm": 0}
uploads = {"tags": [], "folders": []}

def route(r, req):
    u = req.url
    if "api.cloudinary.com" in u:
        try:
            raw = req.post_data_buffer
            pd = (raw.decode("utf-8", "ignore") if raw else (req.post_data or ""))
            for key, bag in (("tags", uploads["tags"]), ("folder", uploads["folders"])):
                m = pd.split('name="%s"' % key)
                if len(m) > 1: bag.append(m[1].split("\r\n\r\n")[1].split("\r\n")[0])
        except Exception as ex: uploads["tags"].append("HATA:" + str(ex)[:40])
        r.fulfill(status=200, content_type="application/json",
                  body=json.dumps({"public_id": "booth360/ticari-test/v1", "version": 1725500000, "duration": 15.2})); return
    if "res.cloudinary.com" in u:
        if req.method == "HEAD":
            r.fulfill(status=200, headers={"access-control-allow-origin": "*", "content-type": "video/webm",
                                           "accept-ranges": "bytes", "content-length": str(len(TINY))}, body=""); return
        r.fulfill(status=200, headers={"access-control-allow-origin": "*", "accept-ranges": "bytes"},
                  content_type="video/webm", body=TINY); return
    r.continue_()

res = []
def ok(n, c, extra=""):
    res.append((n, bool(c), extra)); print(("  ✔ " if c else "  ✘ ") + n + (("  — " + extra) if extra else ""))

with sync_playwright() as p:
    br = p.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
                                 "--autoplay-policy=no-user-gesture-required"])
    ctx = br.new_context(viewport={"width": 430, "height": 932}, permissions=["camera"])
    ctx.add_init_script("try{localStorage.setItem('booth360.v1',JSON.stringify(" + json.dumps(INIT) + "))}catch(e){}")
    ctx.route("**/*cloudinary.com/**", route)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("dialog", lambda d: d.dismiss())
    pg.goto(BASE + "index.html"); pg.wait_for_selector("#s-attract.on")
    print("sürüm:", pg.evaluate("B360.VER"))

    # ---- 1) TL hesabı doğru mu (HD: 250 çıktı saniyesi = 1 kredi)
    tl = pg.evaluate("B360.snTl(250)")
    ok("250 sn = 1 kredi = 21,31 TL", abs(tl - 21.31) < 0.01, "%.2f TL" % tl)
    tl18 = pg.evaluate("B360.snTl(18)")
    ok("18 sn'lik bir edit ≈ 1,53 TL", abs(tl18 - 1.534) < 0.01, "%.3f TL" % tl18)

    # ---- 2) çekim yap, iki şablon önizle → iki render sayılmalı
    pg.click("#startBtn"); pg.wait_for_selector("#s-style.on", timeout=25000)
    pg.click("#styleGrid .stcard[data-tpl=yildiz]"); pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    pg.click("#otherBtn"); pg.wait_for_selector("#s-style.on")
    pg.click("#styleGrid .stcard[data-tpl=kalp]"); pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    sy = pg.evaluate("B360.tani().sayac['ticari-test']") or {}
    ok("iki şablon denendi → iki bulut render sayıldı", sy.get("render") == 2, "render=%s, %s sn" % (sy.get("render"), sy.get("sn")))

    # ---- 3) AYNI şablona geri dönmek ikinci kez ücretlendirilmemeli (Cloudinary tekrar saymaz)
    pg.click("#otherBtn"); pg.wait_for_selector("#s-style.on")
    pg.click("#styleGrid .stcard[data-tpl=yildiz]"); pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    sy2 = pg.evaluate("B360.tani().sayac['ticari-test']") or {}
    ok("aynı şablona dönüş TEKRAR ücretlendirilmiyor", sy2.get("render") == 2, "render=%s" % sy2.get("render"))

    # ---- 4) maliyet metni TL yazıyor
    mm = pg.evaluate("B360.maliyetMetin()")
    ok("maliyet metni TL gösteriyor", "TL" in mm and "kredi" in mm, mm[:80])

    pg.click("#useBtn"); pg.wait_for_selector("#s-done.on")

    # ---- 5) DENEME MODU: sayaç ve galeri etiketi kirlenmemeli
    pg.click("#againBtn"); pg.wait_for_selector("#s-attract.on")
    once = dict(pg.evaluate("B360.tani().sayac['ticari-test']") or {})
    uploads["tags"].clear(); uploads["folders"].clear()
    pg.evaluate("B360.S.deneme=1;B360.save()")
    pg.click("#startBtn"); pg.wait_for_selector("#s-style.on", timeout=25000)
    pg.click("#styleGrid .stcard[data-tpl=yildiz]"); pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    pg.click("#useBtn"); pg.wait_for_selector("#s-done.on")
    sonra = dict(pg.evaluate("B360.tani().sayac['ticari-test']") or {})
    ok("deneme modu: çekim sayacı artmadı", sonra.get("cekim") == once.get("cekim"),
       "%s → %s" % (once.get("cekim"), sonra.get("cekim")))
    ok("deneme modu: teslim sayacı artmadı", sonra.get("teslim") == once.get("teslim"))
    ok("deneme modu: maliyet sayacı artmadı", sonra.get("render") == once.get("render"),
       "render %s → %s" % (once.get("render"), sonra.get("render")))
    ok("deneme modu: video _deneme klasörüne gitti", uploads["folders"] and uploads["folders"][-1] == "booth360/_deneme",
       str(uploads["folders"][-1:]))
    ok("deneme modu: etkinlik galerisi etiketi verilmedi", uploads["tags"] and uploads["tags"][-1] == "deneme-360",
       str(uploads["tags"][-1:]))
    pg.evaluate("B360.S.deneme=0;B360.save()")

    # ---- 6) PANEL ŞİFRESİ değiştirilebiliyor
    pg.click("#againBtn"); pg.wait_for_selector("#s-attract.on")
    pg.evaluate("B360.S.pin='7391';B360.save()")
    ok("şifre ayardan okunuyor", pg.evaluate("B360.PINK()") == "7391")
    pg.click("#gearBtn"); pg.wait_for_selector("#s-pin.on")
    for d in "1234": pg.click("#pinPad button:has-text('%s')" % d)
    pg.wait_for_timeout(300)
    ok("eski şifre (1234) artık panele sokmuyor", "on" not in (pg.get_attribute("#s-admin", "class") or ""))
    for d in "7391": pg.click("#pinPad button:has-text('%s')" % d)
    pg.wait_for_selector("#s-admin.on", timeout=5000)
    ok("yeni şifre panele sokuyor", True)
    ok("bozuk şifre varsayılana düşüyor", pg.evaluate("B360.S.pin='ab';B360.PINK()") == "1234")
    pg.evaluate("B360.S.pin='1234';B360.save()")

    # ---- 7) AYAR YEDEĞİ: metin doğru, sayaç taşınmıyor
    kod = json.loads(pg.evaluate("B360.ayarKod()"))
    ok("ayar metni etkinlik ve cloud bilgisini taşıyor", kod.get("evt") == "Ticari Test" and kod.get("cldName") == "rqhgtbvd")
    ok("ayar metni sayacı TAŞIMIYOR (başka cihaza yanlış rakam gitmesin)", "sayac" not in kod)
    bag = pg.evaluate("B360.ayarBag()")
    ok("yer imi bağlantısı https ve #ayar= içeriyor", bag.startswith("http") and "#ayar=" in bag, bag[:52] + "…")

    # ---- 8) HAFIZA SİLİNDİ senaryosu: bağlantıdan ayarlar geri geliyor mu
    bag_local = bag.replace("https://burakisik88-ctrl.github.io/booth360/", BASE)
    pg.evaluate("B360.S.evt='SİLİNDİ';B360.S.cldName='yok';B360.save()")
    p2 = ctx.new_page(); e2 = []
    p2.on("pageerror", lambda e: e2.append(str(e)))
    p2.add_init_script("try{localStorage.removeItem('booth360.v1')}catch(e){}")
    p2.goto(bag_local); p2.wait_for_selector("#s-attract.on")
    ok("hafıza silinmiş cihaz: bağlantıdan ayar yüklendi", p2.evaluate("B360.tani().ayarGeldi") is True)
    ok("hafıza silinmiş cihaz: etkinlik adı geri geldi", p2.evaluate("B360.S.evt") == "Ticari Test", p2.evaluate("B360.S.evt"))
    ok("hafıza silinmiş cihaz: Cloudinary ayarı geri geldi", p2.evaluate("B360.S.cldName") == "rqhgtbvd")
    ok("bağlantıdaki ayar adres çubuğunda kalmıyor (misafir görmesin)", "#ayar=" not in p2.evaluate("location.hash"))
    ok("kurtarma sayfasında JS hatası yok", not e2, "; ".join(e2)[:150])
    p2.close()

    # ---- 9) elle yapıştırılan ayar yükleniyor, bozuk metin reddediliyor
    pg.evaluate("B360.S.evt='X';B360.save()")
    hata = pg.evaluate("B360.ayarUygula('bu json degil')")
    ok("bozuk ayar metni reddediliyor", bool(hata), hata[:50])
    ok("bozuk metin ayarları bozmadı", pg.evaluate("B360.S.evt") == "X")
    pg.evaluate("B360.ayarUygula(%s)" % json.dumps(json.dumps(kod)))
    ok("geçerli ayar metni yükleniyor", pg.evaluate("B360.S.evt") == "Ticari Test")

    ok("JS hatası yok", not errs, "; ".join(errs)[:200])
    br.close()

bad = [r for r in res if not r[1]]
print(f"\nSONUÇ: {len(res)-len(bad)}/{len(res)} geçti" + (" — HATALAR: " + ", ".join(r[0] for r in bad) if bad else ""))
sys.exit(1 if bad else 0)
