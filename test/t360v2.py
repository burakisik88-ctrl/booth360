#!/usr/bin/env python3
"""OBSKURA 360 v0.2 — uçtan uca test (sahte kamera, Cloudinary taklidi).
   Doğruladığı şeyler: kayıt→yükleme→şablon kartları→423 yoklama→önizleme→QR (izleme sayfası)→v.html aynı URL'yi kuruyor,
   panel (şablon seç, bayraklar, kalibrasyon), hata yolu (400), URL uzunlukları."""
import json, sys, time, threading, http.server, socketserver, pathlib, functools
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "test" / "shots"; SHOTS.mkdir(parents=True, exist_ok=True)
PORT = 8360
TINY = pathlib.Path("/tmp/tiny.mp4").read_bytes()
BASE = f"http://localhost:{PORT}/"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    h = functools.partial(Quiet, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), h) as httpd:
        httpd.serve_forever()
threading.Thread(target=serve, daemon=True).start()
time.sleep(0.4)

INIT_S = {"evt": "Deneme Gecesi", "sure": 5, "cldName": "rqhgtbvd", "cldPreset": "booth_qr",
          "muzikler": [{"n": "track1", "pid": "booth360/_muzik/track1"}, {"n": "track2", "pid": "booth360/_muzik/track2"}],
          "muzikSec": "booth360/_muzik/track1", "tplMusic": {"kalp": "booth360/_muzik/track2"},
          "logoPid": "booth360/_logo/yopi", "fxHave": {"yildiz": 1, "kalp": 1, "konfeti": 1, "sparkle": 1},
          "turSn": 10, "yuzSn": 0}
head_hits = {}
results = []
def ok(name, cond, extra=""):
    results.append((name, bool(cond), extra))
    print(("  ✔ " if cond else "  ✘ ") + name + (("  — " + extra) if extra else ""))

def route_cld(route, request):
    url = request.url
    if "api.cloudinary.com" in url and "/upload" in url:
        kind = "video" if "/video/upload" in url else "image"
        body = {"public_id": "booth360/deneme-gecesi/abc123" if kind == "video" else "booth360/_logo/x", "version": 1725500000, "duration": 15.2}
        route.fulfill(status=200, content_type="application/json", body=json.dumps(body)); return
    if "res.cloudinary.com" in url:
        if "so_0,eo_8.8/" in url:  # Sinema Noir → kasıtlı 400 (hata yolu testi)
            route.fulfill(status=400, headers={"access-control-allow-origin": "*", "x-cld-error": "Invalid transformation"}, body=""); return
        if request.method == "HEAD":
            n = head_hits.get(url, 0) + 1; head_hits[url] = n
            if n <= 2:
                route.fulfill(status=423, headers={"access-control-allow-origin": "*"}, body=""); return
            route.fulfill(status=200, headers={"access-control-allow-origin": "*", "content-type": "video/webm", "accept-ranges": "bytes", "content-length": str(len(TINY))}, body=""); return
        route.fulfill(status=200, headers={"access-control-allow-origin": "*", "accept-ranges": "bytes"}, content_type="video/webm", body=TINY); return
    route.continue_()

with sync_playwright() as p:
    br = p.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream", "--autoplay-policy=no-user-gesture-required"])
    ctx = br.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2, permissions=["camera"])
    ctx.add_init_script("try{localStorage.setItem('booth360.v1',JSON.stringify(" + json.dumps(INIT_S) + "))}catch(e){}")
    ctx.route("**/*cloudinary.com/**", route_cld)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "index.html")
    pg.wait_for_selector("#s-attract.on")
    ok("sayfa açıldı, sürüm okundu", bool(str(pg.evaluate("window.B360&&B360.VER")).startswith("v0.")), str(pg.evaluate("window.B360&&B360.VER")))

    # --- kayıt → yükleme → şablonlar
    pg.click("#startBtn")
    pg.wait_for_selector("#s-style.on", timeout=25000)
    cards = pg.query_selector_all("#styleGrid .stcard")
    tpl_cards = [c for c in cards if c.get_attribute("data-tpl") != "ham"]
    ok("6 şablon kartı + 'Şablonsuz' seçeneği", len(tpl_cards) == 6 and len(cards) == 7,
       f"{len(tpl_cards)} şablon + {len(cards)-len(tpl_cards)} şablonsuz")
    ok("kartlarda hız şeridi", pg.evaluate("document.querySelectorAll('#styleGrid .sb i').length") >= 20)
    ok("müzik çipi açık", pg.evaluate("document.querySelector('#muzikChip').textContent").endswith("AÇIK"))
    warm_url = pg.evaluate("B360.tplUrl('yildiz')")
    time.sleep(0.6)
    ok("ilk şablon arka planda ısıtıldı (HEAD)", head_hits.get(warm_url, 0) >= 1, f"HEAD sayısı {head_hits.get(warm_url,0)}")
    pg.screenshot(path=str(SHOTS / "1_sablonlar.png"))

    # --- URL biçimleri
    urls = {t: pg.evaluate(f"B360.tplUrl('{t}')") for t in ["yildiz", "kalp", "konfeti", "noir", "geri", "kulup"]}
    u = urls["yildiz"]
    ok("yildiz: 4 splice + ¼× + FX yeşil perde + logo + müzik du_ + q_auto",
       u.count(",fl_splice/") == 4 and "fl_splice,fl_layer_apply" not in u and ",fl_splice/e_accelerate:-50/" in u and "e_make_transparent:25,co_rgb:00ff00" in u
       and "l_booth360:_logo:yopi/c_scale,w_0.22,fl_relative/fl_layer_apply,g_north_east" in u and "l_audio:booth360:_muzik:track1,du_" in u and "c_pad,w_1080,h_1920,b_rgb:0D0B0A" in u and "b_blurred" not in u and u.endswith("/q_auto/v1725500000/booth360/deneme-gecesi/abc123.mp4"))
    ok("kalp: şablona özel müzik (track2)", "l_audio:booth360:_muzik:track2,du_" in urls["kalp"])
    ok("konfeti: flaş + geri sarım", "e_brightness:90" in urls["konfeti"] and "e_reverse" in urls["konfeti"])
    ok("noir: gri + FX yok + gren kapalı", "e_grayscale" in urls["noir"] and "_fx:" not in urls["noir"] and "e_noise" not in urls["noir"])
    ok("geri: tüm tur tersten", "so_0,eo_15.2,e_accelerate:100,fl_splice/e_reverse" in urls["geri"])
    ok("kulup: zoom + flaş, URL < 2000", "c_crop,w_0.85,h_0.85,g_center" in urls["kulup"] and "e_brightness:90" in urls["kulup"] and len(urls["kulup"]) < 2000, f"{len(urls['kulup'])} karakter")
    ok("hız aralığı −50…100 dışında değer yok", all(-50 <= int(x) <= 100 for uu in urls.values() for x in __import__('re').findall(r"e_accelerate:(-?\d+)", uu)))
    (ROOT / "test" / "urls_v02.txt").write_text("\n\n".join(f"{k}:\n{v}" for k, v in urls.items()), encoding="utf-8")

    # --- önizleme (423→423→200) → QR
    pg.click("#styleGrid .stcard[data-tpl=yildiz]")
    pg.wait_for_selector("#s-prev.on")
    pg.wait_for_function("!document.querySelector('#useBtn').disabled", timeout=30000)
    ok("423 yoklaması sonra video yüklendi", head_hits.get(u, 0) >= 3 and pg.evaluate("document.querySelector('#prevBusy').style.display") == "none", f"HEAD {head_hits.get(u,0)}")
    pg.screenshot(path=str(SHOTS / "2_onizleme.png"))
    pg.click("#useBtn")
    pg.wait_for_selector("#s-done.on")
    last = pg.evaluate("B360.last()")
    ok("QR izleme sayfasına gidiyor", last["page"].startswith(BASE + "v.html#") and len(last["page"]) < 260, f"{len(last['page'])} karakter")
    ok("QR çizildi", pg.evaluate("(function(){var c=document.querySelector('#qrCanvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,k=0;for(var i=0;i<d.length;i+=4)if(d[i]<60)k++;return k})()") > 5000)
    pg.screenshot(path=str(SHOTS / "3_qr.png"))

    # --- v.html aynı URL'yi kuruyor mu
    pv = ctx.new_page(); pv.on("pageerror", lambda e: errs.append("v.html: " + str(e)))
    pv.goto(last["page"])
    pv.wait_for_function("!document.querySelector('#saveBtn').disabled", timeout=30000)
    ok("v.html aynı Cloudinary URL'sini üretti", pv.evaluate("B360V.url") == last["url"])
    pv.screenshot(path=str(SHOTS / "4_izleme_sayfasi.png"))
    pv.close()

    # --- hata yolu: noir 400
    pg.click("#againBtn"); pg.wait_for_selector("#s-attract.on")
    pg.evaluate("B360.setVid({pid:'booth360/deneme-gecesi/abc123',ver:1725500000,dur:15.2});B360.muzik(true);B360.buildStyleGrid();B360.go('style')")
    pg.click("#styleGrid .stcard[data-tpl=noir]")
    pg.wait_for_function("document.querySelector('#prevBusy .lede').textContent.indexOf('hazırlanamadı')>=0", timeout=15000)
    ok("400 → 'hazırlanamadı' mesajı", True)
    pg.click("#otherBtn"); pg.wait_for_selector("#s-style.on")

    # --- panel
    pg.click("#yenidenBtn"); pg.wait_for_selector("#s-attract.on")
    pg.click("#gearBtn"); pg.wait_for_selector("#s-pin.on")
    for k in "1234": pg.click(f"#pinPad button:text-is('{k}')")
    pg.wait_for_selector("#s-admin.on")
    ok("panelde 6 şablon satırı", pg.evaluate("document.querySelectorAll('#tplList .mrow').length") == 6)
    pg.screenshot(path=str(SHOTS / "5_panel.png"), full_page=True)
    pg.evaluate("document.querySelectorAll('#tplList .mrow input')[5].click()")
    ok("şablon kapatınca aktif=5", pg.evaluate("B360.S.aktif.length") == 5)
    pg.evaluate("document.querySelector('#fkDbl').click()")
    ok("¼× bayrağı kapandı → URL'de çift -50 yok", pg.evaluate("B360.S.flags.dbl") == 0 and ",fl_splice/e_accelerate:-50/" not in pg.evaluate("B360.setVid({pid:'x/y',ver:1,dur:15});B360.tplUrl('yildiz')"))
    pg.evaluate("document.querySelector('#fkDbl').click()")
    # kalibrasyon: 4 sn'lik deneme videosuyla
    pg.evaluate("fetch('/../../tmp/tiny.mp4').catch(function(){})")
    pg.evaluate("(async()=>{const r=await fetch('" + BASE + "test/tiny.mp4');const b=await r.blob();B360.keepBlob(b);B360.openCal()})()")
    pg.wait_for_selector("#s-cal.on")
    pg.wait_for_function("document.querySelector('#calVid').currentTime>0.3", timeout=10000)
    pg.click("#calFace"); t1 = pg.evaluate("document.querySelector('#calVid').currentTime")
    pg.wait_for_function(f"document.querySelector('#calVid').currentTime>{t1}+1.8", timeout=10000)
    pg.click("#calFace")
    pg.screenshot(path=str(SHOTS / "6_kalibrasyon.png"))
    pg.click("#calSave"); pg.wait_for_selector("#s-admin.on")
    ok("kalibrasyon kaydedildi (yüz anı + tur süresi)", pg.evaluate("B360.S.turSn") > 1.5 and pg.evaluate("B360.S.yuzSn") >= 0, f"yüz {pg.evaluate('B360.S.yuzSn')} sn, tur {pg.evaluate('B360.S.turSn')} sn")
    # QR mp4 modu
    pg.select_option("#fQr", "mp4"); ok("QR modu mp4 kaydedildi", pg.evaluate("B360.S.qrMod") == "mp4")
    pg.select_option("#fQr", "page")

    # --- paket: efektsiz (şablon var, FX yok)
    pg.select_option("#fPaket", "sablon")
    u_sablon = pg.evaluate("B360.setVid({pid:'booth360/deneme-gecesi/abc123',ver:1725500000,dur:15.2});B360.tplUrl('yildiz')")
    ok("efektsiz paket: FX katmanı yok ama şablon çalışıyor",
       "_fx:" not in u_sablon and u_sablon.count(",fl_splice/") == 4 and "e_saturation:15" in u_sablon)
    pg.select_option("#fPaket", "efektli")
    u_efektli = pg.evaluate("B360.tplUrl('yildiz')")
    ok("efektli paket: FX katmanı geri geliyor", "l_video:booth360:_fx:yildiz" in u_efektli)

    # --- editsiz paket: yükleme → doğrudan karekod, ham adres
    pg.select_option("#fPaket", "editsiz")
    pg.click("#s-admin .iconbtn"); pg.wait_for_selector("#s-attract.on")
    pg.click("#startBtn"); pg.wait_for_selector("#s-done.on", timeout=25000)
    lastH = pg.evaluate("B360.last()")
    ok("editsiz: yükleme sonrası doğrudan karekod, ham mp4 adresi", lastH["url"].endswith("/video/upload/v1725500000/booth360/deneme-gecesi/abc123.mp4") and "t=ham" in lastH["page"])
    pv2 = ctx.new_page(); pv2.goto(lastH["page"]); pv2.wait_for_function("!document.querySelector('#saveBtn').disabled", timeout=30000)
    ok("editsiz: v.html ham adresi kuruyor", pv2.evaluate("B360V.url") == lastH["url"]); pv2.close()
    pg.evaluate("B360.S.paket='efektli';B360.S.mod='editli';B360.save()")
    ok("JS hatası yok", not errs, "; ".join(errs)[:300])
    br.close()

bad = [r for r in results if not r[1]]
print(f"\nSONUÇ: {len(results)-len(bad)}/{len(results)} geçti" + (" — HATALAR: " + ", ".join(r[0] for r in bad) if bad else ""))
sys.exit(1 if bad else 0)
