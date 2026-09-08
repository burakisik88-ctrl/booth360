#!/usr/bin/env python3
"""OBSKURA 360 v0.4 — SAHA TESTİ (yarın hata çıkmasın diye).
   Doğruladığı şeyler: internet kesilince video kaybolmuyor (kuyruk + otomatik tekrar),
   elle tekrar / vazgeç, otomatik başa dönüş, önceki misafirin videosunun silinmesi (KVKK),
   çift dokunma koruması, çekim sayacı, galeri adresi, meşgulken çıkış uyarısı, KVKK metni."""
import json, sys, time, threading, http.server, socketserver, pathlib, functools
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8364
TINY = pathlib.Path("/tmp/tiny.mp4").read_bytes()
BASE = f"http://localhost:{PORT}/"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Quiet, directory=str(ROOT))) as h:
        h.serve_forever()
threading.Thread(target=serve, daemon=True).start(); time.sleep(0.4)

INIT = {"evt": "Saha Testi", "sure": 3, "cldName": "rqhgtbvd", "cldPreset": "booth_qr",
        "muzikler": [], "muzikSec": "", "logoPid": "", "fxHave": {"yildiz": 1, "kalp": 1, "konfeti": 1, "sparkle": 1},
        "turSn": 10, "yuzSn": 0, "otoDon": 3, "paket": "editsiz", "mod": "editsiz", "sayac": {}}

UP = {"fail": 0}          # kaç yükleme isteği reddedilecek
up_calls = {"n": 0}

def route(r, req):
    u = req.url
    if "api.cloudinary.com" in u:
        up_calls["n"] += 1
        if UP["fail"] > 0:
            UP["fail"] -= 1
            r.fulfill(status=503, content_type="application/json", body='{"error":{"message":"gecici"}}'); return
        r.fulfill(status=200, content_type="application/json",
                  body=json.dumps({"public_id": "booth360/saha-testi/vid%d" % up_calls["n"],
                                   "version": 1725500000, "duration": 15.2})); return
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

    # ---- 1) KVKK metni açılış ekranında görünüyor mu (yasal zorunluluk)
    kv = pg.text_content("#kvkkNot") or ""
    ok("açılışta KVKK bilgilendirmesi var", len(kv.strip()) > 20, kv.strip()[:60] + "…")

    # ---- 1b) GİZLİ OLMASI GEREKEN ŞEYLER GERÇEKTEN GİZLİ Mİ?
    #     ('hidden' özniteliği, .btn/.row gibi display: veren sınıflar tarafından eziliyordu —
    #      misafir yüklenirken 'Vazgeç' düğmesini görüyordu ve videoyu iptal edebiliyordu)
    gorunur = pg.evaluate("""(function(){
        var bad=[];
        document.querySelectorAll('[hidden]').forEach(function(el){
            if(getComputedStyle(el).display!=='none')bad.push(el.id||el.className||el.tagName);
        });
        return bad})()""")
    ok("hidden işaretli hiçbir öğe ekranda görünmüyor", not gorunur, ", ".join(gorunur)[:120])
    ok("'Tekrar dene / Vazgeç' satırı normalde gizli (misafir videoyu iptal edemesin)",
       pg.evaluate("getComputedStyle(document.querySelector('#upTekrar')).display") == "none")

    # ---- 2) ÇİFT DOKUNMA: BAŞLAT'a iki kez basınca tek kayıt açılmalı
    pg.click("#startBtn")
    try: pg.click("#startBtn", timeout=600)
    except Exception: pass
    pg.wait_for_selector("#s-rec.on", timeout=15000)
    ok("çift dokunma koruması: BAŞLAT kilitlendi", pg.evaluate("document.querySelector('#startBtn').disabled") is True)

    # ---- 3) kayıt sırasında 'meşgul' bayrağı → sayfadan çıkışa uyarı
    ok("kayıt sırasında sayfa kilidi (meşgul) açık", pg.evaluate("B360.tani().mesgul") is True)


    # ---- 4) yükleme başarılı → karekod, sayaç arttı
    pg.wait_for_selector("#s-done.on", timeout=30000)
    t = pg.evaluate("B360.tani()")
    ok("yükleme bitti, meşgul kalkmış", t["mesgul"] is False)
    ok("bekleyen kuyruk boş (video yüklendi)", t["bekleyen"] is False)
    sy = t["sayac"].get("saha-testi", {})
    ok("çekim sayacı arttı", sy.get("cekim", 0) == 1, "çekim=%s" % sy.get("cekim"))
    ok("teslim (karekod) sayacı arttı", sy.get("teslim", 0) == 1, "teslim=%s" % sy.get("teslim"))
    ok("sayaç metni etkinlik adını yazıyor", "Saha Testi" in (pg.evaluate("B360.sayacMetin()") or ""))

    # ---- 5) OTOMATİK BAŞA DÖNÜŞ (3 sn) — kimse dokunmasa bile sıradaki misafire hazır
    t0 = time.time()
    pg.wait_for_selector("#s-attract.on", timeout=12000)
    ok("otomatik başa dönüş çalıştı", time.time() - t0 < 10, "%.1f sn içinde" % (time.time() - t0))

    # ---- 6) TEMİZLİK (KVKK): başa dönünce önceki misafirin karekodu/videosu ekranda kalmasın
    temiz = pg.evaluate("""(function(){
        var c=document.querySelector('#qrCanvas'),x=c.getContext('2d');
        var d=x.getImageData(0,0,c.width,c.height).data,dolu=0;
        for(var i=3;i<d.length;i+=4){if(d[i]!==0){dolu++;break}}
        var pv=document.querySelector('#prevVid');
        return {qrBos:dolu===0, vidBos:!pv.getAttribute('src'), adres:(document.querySelector('#qrAdres')||{}).textContent||''};
    })()""")
    ok("başa dönünce karekod silindi", temiz["qrBos"] is True)
    ok("başa dönünce önizleme videosu silindi", temiz["vidBos"] is True)
    ok("başa dönünce adres satırı temizlendi", temiz["adres"].strip() == "")

    # ---- 7) İNTERNET KESİLDİ: ilk 2 deneme 503 → kendi kendine tekrar deneyip başarmalı
    UP["fail"] = 2
    n0 = up_calls["n"]
    pg.click("#startBtn")
    pg.wait_for_selector("#s-done.on", timeout=60000)
    ok("bağlantı koptu → otomatik tekrar denedi ve başardı", up_calls["n"] - n0 >= 3,
       "%d istek gitti" % (up_calls["n"] - n0))

    # ---- 8) İNTERNET TAMAMEN YOK: 3 deneme de düşerse video KAYBOLMAMALI
    pg.wait_for_selector("#s-attract.on", timeout=12000)
    UP["fail"] = 99
    pg.click("#startBtn")
    pg.wait_for_selector("#upTekrar:not([hidden])", timeout=90000)
    t = pg.evaluate("B360.tani()")
    ok("yükleme büsbütün düştü → 'Tekrar dene' düğmesi çıktı", True)
    ok("video kuyrukta duruyor (KAYBOLMADI)", t["bekleyen"] is True)
    note = pg.text_content("#upNote") or ""
    ok("kullanıcıya videonun durduğu söyleniyor", "telefonda duruyor" in note, note[:70])

    # ---- 9) ELLE TEKRAR: internet gelince tek dokunuşla yükleniyor
    UP["fail"] = 0
    pg.click("#upTekrarBtn")
    pg.wait_for_selector("#s-done.on", timeout=40000)
    ok("internet gelince 'Tekrar dene' yükledi", pg.evaluate("B360.tani().bekleyen") is False)

    # ---- 10) VAZGEÇ: kuyruğu boşaltıp başa dönmeli
    pg.wait_for_selector("#s-attract.on", timeout=12000)
    UP["fail"] = 99
    pg.click("#startBtn")
    pg.wait_for_selector("#upTekrar:not([hidden])", timeout=90000)
    pg.click("#upVazgec")
    pg.wait_for_selector("#s-attract.on", timeout=8000)
    t = pg.evaluate("B360.tani()")
    ok("vazgeç: kuyruk boşaldı, ekran kilidi açıldı", t["bekleyen"] is False and t["mesgul"] is False)
    UP["fail"] = 0

    # ---- 10b) ŞABLONSUZ KART + LOGO ZORUNLULUĞU + BAŞA DÖN
    pg.evaluate("B360.S.paket='efektli';B360.S.mod='editli';B360.S.logoPid='';B360.S.logoZorunlu=0;B360.S.hamKart=1;B360.S.kadraj='genis916d';B360.save()")
    pg.click("#startBtn"); pg.wait_for_selector("#s-style.on", timeout=25000)
    ok("şablon ekranında 'Şablonsuz' kartı var (misafir mecbur değil)",
       pg.evaluate("!!document.querySelector('#styleGrid .stcard[data-tpl=ham]')"))
    hu = pg.evaluate("B360.tplUrl('ham')")
    ok("logo zorunlu değil → şablonsuz video HİÇ işlenmiyor (0 kredi)",
       "/video/upload/v" in hu and "l_" not in hu.split("/video/upload/")[1], hu[-60:])

    pg.evaluate("B360.S.logoPid='booth360/_logo/yopi';B360.S.logoZorunlu=1;B360.save()")
    hu2 = pg.evaluate("B360.tplUrl('ham')")
    ok("logo zorunlu → şablonsuz videoya logo basılıyor", "l_booth360:_logo:yopi" in hu2)
    ok("logo zorunlu → 9:16 bandı da uygulanıyor", "c_pad,w_1080,h_1920" in hu2)
    ok("şablonsuzda efekt/müzik/hız zinciri YOK",
       "e_accelerate" not in hu2 and "l_audio" not in hu2 and "fl_splice" not in hu2)

    ok("kadraj: düz bant (blur yok)", "b_rgb:0D0B0A" in hu2 and "b_blurred" not in hu2, hu2.split("/")[6] if len(hu2.split("/"))>6 else "")
    pg.evaluate("B360.S.kadraj='genis916k';B360.save()")
    ok("kadraj: 'bant yok' seçilince kırpıyor", "c_fill,w_1080,h_1920" in pg.evaluate("B360.tplUrl('ham')"))
    pg.evaluate("B360.S.kadraj='genis916d';B360.save()")

    # şablonsuz kartı gerçekten çalışıyor mu (önizleme → karekod)
    pg.evaluate("B360.buildStyleGrid()")
    pg.click("#styleGrid .stcard[data-tpl=ham]"); pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    ok("şablonsuz önizleme açıldı", True)
    ok("önizleme ekranında 'Başa dön' düğmesi var",
       pg.evaluate("getComputedStyle(document.querySelector('#prevBasa')).display") != "none")
    pg.click("#prevBasa"); pg.wait_for_selector("#s-attract.on", timeout=8000)
    ok("'Başa dön' sayaç beklemeden başa döndürdü", True)

    pg.evaluate("B360.S.hamKart=0;B360.save()")
    pg.click("#startBtn"); pg.wait_for_selector("#s-style.on", timeout=25000)
    ok("panelden kapatılınca 'Şablonsuz' kartı çıkmıyor",
       pg.evaluate("!document.querySelector('#styleGrid .stcard[data-tpl=ham]')"))
    ok("şablon ekranında da 'Başa dön' var",
       pg.evaluate("getComputedStyle(document.querySelector('#styleBasa')).display") != "none")
    pg.click("#styleBasa"); pg.wait_for_selector("#s-attract.on", timeout=8000)
    pg.evaluate("B360.S.hamKart=1;B360.S.logoZorunlu=0;B360.S.logoPid='';B360.save()")

    # ---- 11) GALERİ ADRESİ doğru kuruluyor mu
    gu = pg.evaluate("B360.galeriUrl()")
    ok("galeri adresi doğru", gu.endswith("g.html#c=rqhgtbvd&t=saha-testi-360&e=Saha%20Testi"), gu[-58:])

    # ---- 12) GALERİ SAYFASI açılıyor ve etkinlik adını yazıyor
    gp = ctx.new_page(); gerrs = []
    gp.on("pageerror", lambda e: gerrs.append(str(e)))
    gp.route("**/res.cloudinary.com/**/video/list/**", lambda r, q: r.fulfill(
        status=200, content_type="application/json", headers={"access-control-allow-origin": "*"},
        body=json.dumps({"resources": [{"public_id": "booth360/saha-testi/vid1", "version": 1725500000, "format": "mp4"},
                                        {"public_id": "booth360/saha-testi/vid2", "version": 1725500001, "format": "mp4"}]})))
    gp.goto(gu.replace(BASE, BASE))
    gp.wait_for_timeout(1500)
    kart = gp.evaluate("document.querySelectorAll('#grid .cell').length")
    gmsg = (gp.text_content("#msg") or "").strip()
    ok("galeri sayfası video kartlarını çizdi", kart >= 2, "%d kart%s" % (kart, ("  msg=" + gmsg[:70]) if kart < 2 else ""))
    ok("galeri altyazısı video sayısını yazıyor", "2 video" in (gp.text_content("#alt") or ""), (gp.text_content("#alt") or "")[:50])
    gp.evaluate("document.querySelector('#grid .cell').click()")
    gp.wait_for_timeout(300)
    ok("galeride karta dokununca oynatıcı açılıyor", "on" in (gp.get_attribute("#lb", "class") or ""))
    ok("galeride JS hatası yok", not gerrs, "; ".join(gerrs)[:150])
    gp.close()

    # ---- 13) panelde saha ayarları duruyor mu
    pg.evaluate("B360.go('admin');B360.fillAdmin&&B360.fillAdmin()")
    alanlar = pg.evaluate("""(function(){var k=['#fOto','#fWake','#fKvkk','#sayacNot','#galeriAc','#sayacSifirla'];
        return k.filter(function(s){return !!document.querySelector(s)}).length})()""")
    ok("panelde saha ayarları eksiksiz", alanlar == 6, "%d/6 alan" % alanlar)

    ok("JS hatası yok", not errs, "; ".join(errs)[:200])
    br.close()

bad = [r for r in res if not r[1]]
print(f"\nSONUÇ: {len(res)-len(bad)}/{len(res)} geçti" + (" — HATALAR: " + ", ".join(r[0] for r in bad) if bad else ""))
sys.exit(1 if bad else 0)
