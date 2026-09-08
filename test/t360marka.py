#!/usr/bin/env python3
"""OBSKURA 360 v0.7 — ÇOK BOOTH + RAPOR + MARKA testi.
   İki booth aynı etkinlikte çalışırken sayaç bölünüyordu; gerçek toplam buluttan okunmalı.
   Ayrıca: müşteri raporu sayfası, markalı açılış ekranı, opsiyonel toplu indirme."""
import json, sys, time, threading, http.server, socketserver, pathlib, functools, datetime
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8370
TINY = pathlib.Path("/tmp/tiny.mp4").read_bytes()
BASE = f"http://localhost:{PORT}/"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Quiet, directory=str(ROOT))) as h:
        h.serve_forever()
threading.Thread(target=serve, daemon=True).start(); time.sleep(0.4)

INIT = {"evt": "Gala Gecesi", "sure": 3, "cldName": "rqhgtbvd", "cldPreset": "booth_qr",
        "muzikler": [], "muzikSec": "", "logoPid": "booth360/_logo/yopi",
        "fxHave": {"yildiz": 1, "kalp": 1, "konfeti": 1, "sparkle": 1},
        "turSn": 10, "yuzSn": 0, "otoDon": 0, "paket": "efektli", "mod": "editli", "sayac": {}, "warm": 0}

# 17 video: 9'u bir booth'tan, 8'i digerinden — bulut ikisini de goruyor
def liste():
    rs = []
    for i in range(17):
        sa = 20 + (0 if i < 4 else (1 if i < 12 else 2))   # 20:xx 4 adet, 21:xx 8 adet (pik), 22:xx 5 adet
        dk = (i * 3) % 60
        rs.append({"public_id": "booth360/gala-gecesi/v%02d" % i, "version": 1725500000 + i,
                   "format": "mp4", "created_at": "2026-09-08T%02d:%02d:00Z" % (sa, dk)})
    return {"resources": rs}

def route(r, req):
    u = req.url
    if "/video/list/" in u:
        if "gala-gecesi-360" in u:
            r.fulfill(status=200, content_type="application/json",
                      headers={"access-control-allow-origin": "*"}, body=json.dumps(liste())); return
        r.fulfill(status=404, headers={"access-control-allow-origin": "*"}, body=""); return
    if "api.cloudinary.com" in u:
        r.fulfill(status=200, content_type="application/json",
                  body=json.dumps({"public_id": "booth360/gala-gecesi/yeni", "version": 1725500099, "duration": 15.2})); return
    if "res.cloudinary.com" in u:
        if req.method == "HEAD":
            r.fulfill(status=200, headers={"access-control-allow-origin": "*", "content-type": "video/mp4",
                                           "accept-ranges": "bytes", "content-length": str(len(TINY))}, body=""); return
        r.fulfill(status=200, headers={"access-control-allow-origin": "*"}, content_type="video/mp4", body=TINY); return
    r.continue_()

res = []
def ok(n, c, extra=""):
    res.append((n, bool(c), extra)); print(("  ✔ " if c else "  ✘ ") + n + (("  — " + extra) if extra else ""))

with sync_playwright() as p:
    br = p.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
                                 "--autoplay-policy=no-user-gesture-required"])
    ctx = br.new_context(viewport={"width": 430, "height": 932}, permissions=["camera"],
                         timezone_id="Europe/Istanbul")
    ctx.add_init_script("try{localStorage.setItem('booth360.v1',JSON.stringify(" + json.dumps(INIT) + "))}catch(e){}")
    ctx.route("**/*cloudinary.com/**", route)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "index.html"); pg.wait_for_selector("#s-attract.on")
    print("sürüm:", pg.evaluate("B360.VER"))

    # ---- 1) ÇOK BOOTH: bu telefonda 2 çekim var, bulutta 17 video
    pg.evaluate("B360.S.sayac={'gala-gecesi':{cekim:2,teslim:2,gun:{}}};B360.save()")
    pg.evaluate("B360.go('admin');B360.fillAdmin()")
    pg.wait_for_function("document.querySelector('#sayacNot').textContent.indexOf('TÜM')>=0", timeout=15000)
    sm = pg.text_content("#sayacNot")
    ok("sayaç bulutdan gerçek toplamı okuyor (17)", "17 video" in sm, sm[:95])
    ok("bu telefonun kendi rakamı da ayrıca yazıyor", "Bu telefon: 2 çekim" in sm)
    ok("hangi rakamın ne olduğu karışmıyor", "TÜM BOOTH" in sm and "Bu telefon" in sm)

    # ---- 2) rapor adresi
    ru = pg.evaluate("B360.raporUrl()")
    ok("rapor adresi doğru kuruluyor", "r.html#c=rqhgtbvd" in ru and "t=gala-gecesi-360" in ru and "&g=" in ru, ru[-60:])

    # ---- 3) RAPOR SAYFASI
    rp = ctx.new_page(); re_ = []
    rp.on("pageerror", lambda e: re_.append(str(e)))
    rp.goto(ru.replace("https://burakisik88-ctrl.github.io/booth360/", BASE))
    rp.wait_for_selector("#icerik:not([hidden])", timeout=20000)
    ok("rapor toplam videoyu yazıyor", "17" in (rp.text_content("#oSayi") or ""), (rp.text_content("#oSayi") or "")[:40])
    pik = rp.text_content("#oPik") or ""
    ok("rapor en yoğun saati buluyor", "8 video" in pik, pik[:45])
    ok("rapor süreyi hesaplıyor", "dk" in (rp.text_content("#oSure") or ""), (rp.text_content("#oSure") or "")[:40])
    ok("rapor tarihi yazıyor", "Eylül 2026" in (rp.text_content("#tarih") or ""), (rp.text_content("#tarih") or "")[:60])
    cub = rp.evaluate("document.querySelectorAll('#cub .s').length")
    ok("saat grafiği çizildi", cub >= 3, "%d sütun" % cub)
    ok("grafikte pik sütunu işaretli", rp.evaluate("document.querySelectorAll('#cub .s.pik').length") == 1)
    ok("grafik ekseninde saat etiketleri var", rp.evaluate("document.querySelectorAll('#eks span').length") == cub)
    ok("rapor etkinlik adını başlığa koyuyor", "Gala Gecesi" in (rp.text_content("#baslik") or ""))
    ok("galeri düğmesi rapora bağlı", "g.html" in (rp.get_attribute("#galeriBtn", "href") or ""))
    ok("raporda JS hatası yok", not re_, "; ".join(re_)[:150])
    rp.close()

    # ---- 4) boş etkinlik raporu çökmüyor
    rp2 = ctx.new_page(); re2 = []
    rp2.on("pageerror", lambda e: re2.append(str(e)))
    rp2.goto(BASE + "r.html#c=rqhgtbvd&t=bos-etkinlik-360&e=Bos")
    rp2.wait_for_selector("#msg:not([hidden])", timeout=15000)
    ok("videosu olmayan etkinlikte rapor düzgün mesaj veriyor", "henüz video yok" in (rp2.text_content("#msg") or ""))
    ok("boş raporda JS hatası yok", not re2, "; ".join(re2)[:120])
    rp2.close()

    # ---- 5) MARKALI AÇILIŞ
    pg.evaluate("""B360.S.ust='ASCENDUM BAYİ TOPLANTISI';B360.S.bas='Anını *yakala*';
                   B360.S.renk='#C8102E';B360.S.markaLogo=1;B360.save();B360.applyBrand()""")
    pg.evaluate("B360.go('attract')")
    ok("üst satır müşteri markasıyla değişti", pg.text_content("#attractUst") == "ASCENDUM BAYİ TOPLANTISI")
    ok("başlık değişti ve *vurgu* uygulandı",
       pg.evaluate("document.querySelector('#attractBas em')?document.querySelector('#attractBas em').textContent:''") == "yakala")
    ok("vurgu rengi uygulandı",
       "200, 16, 46" in pg.evaluate("getComputedStyle(document.querySelector('#attractBas em')).color"),
       pg.evaluate("getComputedStyle(document.querySelector('#attractBas em')).color"))
    ok("açılışta müşteri logosu göründü",
       pg.evaluate("!document.querySelector('#markaLogo').hidden") and
       "booth360/_logo/yopi" in (pg.get_attribute("#markaLogo", "src") or ""))
    pg.evaluate("B360.S.markaLogo=0;B360.save();B360.applyBrand()")
    ok("logo kapatılınca gizleniyor", pg.evaluate("document.querySelector('#markaLogo').hidden") is True)
    pg.evaluate("B360.S.renk='';B360.S.ust='OBSKURA 360';B360.S.bas='Etrafında *dönen* an';B360.save();B360.applyBrand()")
    ok("renk boşaltılınca varsayılana dönüyor",
       "242, 169, 59" in pg.evaluate("getComputedStyle(document.querySelector('#attractBas em')).color"))
    ok("başlıkta HTML enjeksiyonu kaçırılıyor",
       pg.evaluate("""B360.S.bas='<img src=x onerror=alert(1)>*ok*';B360.applyBrand();
                      document.querySelector('#attractBas').querySelectorAll('img').length""") == 0)
    pg.evaluate("B360.S.bas='Etrafında *dönen* an';B360.save();B360.applyBrand()")

    # ---- 6) TOPLU İNDİRME opsiyonel
    ok("varsayılanda galeri adresinde toplu indirme YOK", "&z=1" not in pg.evaluate("B360.galeriUrl()"))
    pg.evaluate("B360.S.zip=1;B360.save()")
    gz = pg.evaluate("B360.galeriUrl()")
    ok("panelden açılınca galeri adresine bayrak ekleniyor", "&z=1" in gz)

    gp = ctx.new_page(); ge = []
    gp.on("pageerror", lambda e: ge.append(str(e)))
    gp.goto(gz.replace("https://burakisik88-ctrl.github.io/booth360/", BASE))
    gp.wait_for_selector("#grid .cell", timeout=15000)
    ok("galeride 'tümünü indir' düğmesi göründü", gp.evaluate("!document.querySelector('#zipRow').hidden"))
    ok("kaç video indirileceğini yazıyor", "17 video" in (gp.text_content("#zipNot") or ""), (gp.text_content("#zipNot") or "")[:50])
    # sadece hash değişince tarayıcı sayfayı yeniden yüklemiyor — zorla yenile
    gp.goto(gz.replace("https://burakisik88-ctrl.github.io/booth360/", BASE).replace("&z=1", ""))
    gp.reload()
    gp.wait_for_selector("#grid .cell", timeout=15000)
    ok("bayrak yokken düğme gizli", gp.evaluate("document.querySelector('#zipRow').hidden") is True)
    ok("galeride JS hatası yok", not ge, "; ".join(ge)[:150])
    gp.close()

    ok("JS hatası yok", not errs, "; ".join(errs)[:200])
    br.close()

bad = [r for r in res if not r[1]]
print(f"\nSONUÇ: {len(res)-len(bad)}/{len(res)} geçti" + (" — HATALAR: " + ", ".join(r[0] for r in bad) if bad else ""))
sys.exit(1 if bad else 0)
