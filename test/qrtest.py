#!/usr/bin/env python3
"""QR denetimi: uygulamanın çizdiği karekod gerçekten okunuyor mu, içinde doğru adres var mı?
   Karekod canvas'ı PNG olarak alınır, OpenCV ile ÇÖZÜLÜR ve beklenen adresle karşılaştırılır."""
import json, sys, time, threading, http.server, socketserver, pathlib, functools, base64
import numpy as np, cv2
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "test" / "shots"; SHOTS.mkdir(parents=True, exist_ok=True)
PORT = 8362
TINY = pathlib.Path("/tmp/tiny.mp4").read_bytes()
BASE = f"http://localhost:{PORT}/"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Quiet, directory=str(ROOT))) as h:
        h.serve_forever()
threading.Thread(target=serve, daemon=True).start(); time.sleep(0.4)

INIT = {"evt": "Deneme Gecesi", "sure": 5, "cldName": "rqhgtbvd", "cldPreset": "booth_qr",
        "muzikler": [{"n": "t1", "pid": "booth360/_muzik/track1"}], "muzikSec": "booth360/_muzik/track1",
        "logoPid": "booth360/_logo/yopi", "fxHave": {"yildiz": 1, "kalp": 1, "konfeti": 1, "sparkle": 1},
        "turSn": 10, "yuzSn": 0}

def route(r, req):
    u = req.url
    if "api.cloudinary.com" in u:
        r.fulfill(status=200, content_type="application/json",
                  body=json.dumps({"public_id": "booth360/deneme-gecesi/abc123", "version": 1725500000, "duration": 15.2})); return
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

def decode_qr(pg, name):
    """canvas → PNG → OpenCV ile karekodu çöz"""
    b64 = pg.evaluate("document.querySelector('#qrCanvas').toDataURL('image/png').split(',')[1]")
    raw = base64.b64decode(b64)
    (SHOTS / name).write_bytes(raw)
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
    big = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    txt, pts, _ = cv2.QRCodeDetector().detectAndDecode(big)
    return txt, img.shape

def decode_kamera(pg, name):
    """GERÇEK KOŞUL BENZETİMİ: ekranda 260 px görünen karekodu, hafif eğik ve bulanık
       bir telefon fotoğrafı gibi işleyip öyle çözmeye çalışır (JPEG sıkıştırma dahil)."""
    b64 = pg.evaluate("document.querySelector('#qrCanvas').toDataURL('image/png').split(',')[1]")
    img = cv2.imdecode(np.frombuffer(base64.b64decode(b64), np.uint8), cv2.IMREAD_GRAYSCALE)
    small = cv2.resize(img, (260, 260), interpolation=cv2.INTER_AREA)      # ekrandaki gerçek boyut
    pad = cv2.copyMakeBorder(small, 60, 60, 60, 60, cv2.BORDER_CONSTANT, value=200)  # gri ortam
    M = cv2.getRotationMatrix2D((pad.shape[1] / 2, pad.shape[0] / 2), 7, 1.0)        # 7° eğik tutuş
    rot = cv2.warpAffine(pad, M, (pad.shape[1], pad.shape[0]), borderValue=200)
    blur = cv2.GaussianBlur(rot, (3, 3), 0.8)                                        # odak kayması
    ok_, enc = cv2.imencode(".jpg", blur, [cv2.IMWRITE_JPEG_QUALITY, 60])            # kamera sıkıştırması
    photo = cv2.imdecode(enc, cv2.IMREAD_GRAYSCALE)
    (SHOTS / name).write_bytes(enc.tobytes())
    txt, _, _ = cv2.QRCodeDetector().detectAndDecode(photo)
    return txt

with sync_playwright() as p:
    br = p.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
                                 "--autoplay-policy=no-user-gesture-required"])
    ctx = br.new_context(viewport={"width": 430, "height": 932}, permissions=["camera"])
    ctx.add_init_script("try{localStorage.setItem('booth360.v1',JSON.stringify(" + json.dumps(INIT) + "))}catch(e){}")
    ctx.route("**/*cloudinary.com/**", route)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "index.html"); pg.wait_for_selector("#s-attract.on")
    print("sürüm:", pg.evaluate("B360.VER"))

    # ---- 1) EDİTLİ · EFEKTLİ paket: şablon seç → karekod
    pg.evaluate("B360.S.paket='efektli';B360.save()")
    pg.click("#startBtn"); pg.wait_for_selector("#s-style.on", timeout=25000)
    pg.click("#styleGrid .stcard[data-tpl=yildiz]"); pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    pg.click("#useBtn"); pg.wait_for_selector("#s-done.on")
    last = pg.evaluate("B360.last()")
    txt, shape = decode_qr(pg, "qr_efektli.png")
    ok("efektli: karekod okunuyor", bool(txt), f"{shape[0]}×{shape[1]} px, çözülen {len(txt)} karakter")
    ok("efektli: karekod içindeki adres doğru", txt == last["page"], (txt[:70] + "…") if txt else "ÇÖZÜLEMEDİ")

    # ---- 2) EDİTSİZ paket: yükleme → doğrudan karekod
    pg.click("#againBtn"); pg.wait_for_selector("#s-attract.on")
    pg.evaluate("B360.S.paket='editsiz';B360.S.mod='editsiz';B360.save()")
    pg.click("#startBtn"); pg.wait_for_selector("#s-done.on", timeout=25000)
    lastH = pg.evaluate("B360.last()")
    txt2, shape2 = decode_qr(pg, "qr_editsiz.png")
    ok("editsiz: karekod okunuyor", bool(txt2), f"çözülen {len(txt2)} karakter")
    ok("editsiz: karekod içindeki adres doğru", txt2 == lastH["page"], (txt2[:70] + "…") if txt2 else "ÇÖZÜLEMEDİ")

    # ---- 3) mp4 modu (uzun adres) — karekod hâlâ okunabiliyor mu?
    pg.click("#againBtn"); pg.wait_for_selector("#s-attract.on")
    pg.evaluate("B360.S.paket='efektli';B360.S.mod='editli';B360.S.qrMod='mp4';B360.save()")
    pg.click("#startBtn"); pg.wait_for_selector("#s-style.on", timeout=25000)
    pg.click("#styleGrid .stcard[data-tpl=yildiz]"); pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    pg.click("#useBtn"); pg.wait_for_selector("#s-done.on")
    last3 = pg.evaluate("B360.last()")
    txt3, shape3 = decode_qr(pg, "qr_mp4.png")
    ok("mp4 modu: uzun adresli karekod okunuyor", bool(txt3), f"adres {len(last3['url'])} karakter, çözülen {len(txt3)}")
    ok("mp4 modu: adres doğru", txt3 == last3["url"], (txt3[:70] + "…") if txt3 else "ÇÖZÜLEMEDİ")

    # ---- 4) gerçek etkinlik adı (Türkçe karakter) ile karekod
    pg.click("#againBtn"); pg.wait_for_selector("#s-attract.on")
    pg.evaluate("B360.S.qrMod='page';B360.S.evt='Şükrü & Gülşah Düğünü';B360.save()")
    pg.click("#startBtn"); pg.wait_for_selector("#s-style.on", timeout=25000)
    pg.click("#styleGrid .stcard[data-tpl=kalp]"); pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    pg.click("#useBtn"); pg.wait_for_selector("#s-done.on")
    last4 = pg.evaluate("B360.last()")
    txt4, _ = decode_qr(pg, "qr_turkce.png")
    ok("Türkçe etkinlik adı: karekod doğru", txt4 == last4["page"], (txt4[:70] + "…") if txt4 else "ÇÖZÜLEMEDİ")

    # ---- 5) TELEFON KAMERASI BENZETİMİ (260 px, 7° eğik, bulanık, JPEG)
    cam = decode_kamera(pg, "qr_kamera.jpg")
    ok("telefon kamerası benzetimi: karekod okundu", cam == last4["page"],
       (cam[:60] + "…") if cam else "OKUNAMADI — karekod büyütülmeli/kontrast artırılmalı")

    # ---- 6) file:// ile açılırsa karekod yine https adres taşımalı
    pf = ctx.new_page(); pf.on("pageerror", lambda e: errs.append("file: " + str(e)))
    pf.goto("file://" + str(ROOT / "index.html"))
    base_file = pf.evaluate("B360.pageUrl?'':''; (function(){var u=B360.setVid({pid:'booth360/x/y',ver:1,dur:15})||B360.pageUrl('yildiz');return u})()")
    ok("file:// açılışta karekod adresi https kalıyor", str(base_file).startswith("https://"), str(base_file)[:60])
    pf.close()

    ok("JS hatası yok", not errs, "; ".join(errs)[:200])
    br.close()

bad = [r for r in res if not r[1]]
print(f"\nSONUÇ: {len(res)-len(bad)}/{len(res)} geçti" + (" — HATALAR: " + ", ".join(r[0] for r in bad) if bad else ""))
sys.exit(1 if bad else 0)
