#!/usr/bin/env python3
"""OBSKURA 360 — SAHA SERTLEŞTİRME 2 (20 Eyl 2026'da yeniden yazıldı).
   Gece 23:00'te düğünde canı yakan şeyler: ana ekrana ekleme (PWA), etkinlik adının
   klasör/etiket/galeri zincirine dönüşü, ikinci booth'a ayar aktarımı, uyku/ses/oto-dön
   ayarları, deneme modu, misafir sayfası ve müşteri raporu.
   Ana çekim akışı → t360saha · sayım ayrımı → t360ayrim · ticari katman → t360ticari."""
import sys, json, time, threading, http.server, socketserver, pathlib, functools, datetime
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8408; BASE = f"http://localhost:{PORT}/"
TINY = pathlib.Path(__file__).resolve().parent.joinpath("tiny.mp4").read_bytes()

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=str(ROOT))) as h:
        h.serve_forever()
threading.Thread(target=serve, daemon=True).start(); time.sleep(0.4)

ok = 0; bad = 0; dusen = []
def T(n, c, e=""):
    global ok, bad
    if c: ok += 1; print(f"  ✔ {n}" + (f"  — {e}" if e else ""))
    else: bad += 1; dusen.append(n); print(f"  ✘ {n}  — {e}")

DUN = (datetime.date.today() - datetime.timedelta(days=1)).isoformat() + "T21:10:00Z"
BUGUN = datetime.date.today().isoformat() + "T10:00:00Z"
liste = {"zaman": DUN, "sayi": 3}
uploads = {"folder": [], "tags": []}

INIT = {"evt": "Saha Testi 2", "sure": 3, "cldName": "rqhgtbvd", "cldPreset": "booth_qr",
        "muzikler": [], "muzikSec": "", "logoPid": "", "fxHave": {}, "turSn": 10, "yuzSn": 0,
        "otoDon": 0, "paket": "editsiz", "mod": "editsiz", "sayac": {}, "warm": 0, "deneme": 0}

def route(r, req):
    u = req.url
    if "api.cloudinary.com" in u:
        try:
            raw = req.post_data_buffer
            pd = (raw.decode("utf-8", "ignore") if raw else (req.post_data or ""))
            for key, bag in (("tags", uploads["tags"]), ("folder", uploads["folder"])):
                m = pd.split('name="%s"' % key)
                if len(m) > 1: bag.append(m[1].split("\r\n\r\n")[1].split("\r\n")[0])
        except Exception as ex: uploads["tags"].append("HATA:" + str(ex)[:40])
        r.fulfill(status=200, content_type="application/json",
                  body=json.dumps({"public_id": "booth360/_deneme/xyz", "version": 1725500000, "duration": 3.0})); return
    if "/video/list/" in u:
        kay = [{"public_id": f"booth360/saha-testi-2/v{i}", "created_at": liste["zaman"], "duration": 15}
               for i in range(liste["sayi"])]
        r.fulfill(status=200, headers={"access-control-allow-origin": "*"},
                  content_type="application/json", body=json.dumps({"resources": kay})); return
    if "res.cloudinary.com" in u:
        if req.method == "HEAD":
            r.fulfill(status=200, headers={"access-control-allow-origin": "*", "content-type": "video/webm",
                                           "accept-ranges": "bytes", "content-length": str(len(TINY))}, body=""); return
        r.fulfill(status=200, headers={"access-control-allow-origin": "*", "accept-ranges": "bytes"},
                  content_type="video/webm", body=TINY); return
    r.continue_()

with sync_playwright() as p:
    br = p.chromium.launch(args=["--no-sandbox", "--use-fake-ui-for-media-stream",
                                 "--use-fake-device-for-media-stream", "--autoplay-policy=no-user-gesture-required"])
    ctx = br.new_context(viewport={"width": 430, "height": 932}, permissions=["camera"])
    ctx.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    ctx.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    ctx.route("**/*cloudinary.com/**", route)
    ctx.add_init_script("try{localStorage.setItem('booth360.v1',JSON.stringify(" + json.dumps(INIT) + "))}catch(e){}")
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("dialog", lambda d: d.dismiss())
    pg.goto(BASE + "index.html"); pg.wait_for_selector("#s-attract.on")
    def ev(js): return pg.evaluate(js)
    print("sürüm:", ev("B360.VER"))

    # ---------- 1) ANA EKRANA EKLEME (PWA) — booth telefonunda tarayıcı çubuğu kalmasın ----------
    print("\n[1] PWA — beş sayfa da ana ekrana eklenebiliyor mu")
    for sayfa in ["index.html", "v.html", "g.html", "t.html", "r.html"]:
        d = pg.evaluate("""async (s)=>{const r=await fetch(s,{cache:'no-store'});const t=await r.text();
            return {man:/rel="manifest"\\s+href="manifest.json"/.test(t)||t.indexOf('rel="manifest" href="manifest.json"')>=0,
                    ikon:t.indexOf('ikon.svg')>=0, tema:t.indexOf('name="theme-color"')>=0};}""", sayfa)
        T(f"{sayfa}: manifest + ikon + tema rengi bağlı", d["man"] and d["ikon"] and d["tema"], str(d))
    man = pg.evaluate("async()=>{const r=await fetch('manifest.json',{cache:'no-store'});return await r.json()}")
    T("manifest: tam ekran (standalone)", man.get("display") == "standalone", man.get("display"))
    T("manifest: dikey kilitli (portrait)", man.get("orientation") == "portrait", man.get("orientation"))
    T("manifest: açılış sayfası booth ekranı", man.get("start_url") == "./index.html", man.get("start_url"))
    T("manifest: ikon svg ve maskelenebilir",
      man["icons"][0]["src"] == "ikon.svg" and "maskable" in man["icons"][0].get("purpose", ""), str(man.get("icons")))
    ik = pg.evaluate("async()=>{const r=await fetch('ikon.svg',{cache:'no-store'});return {s:r.status,t:(await r.text()).slice(0,60)}}")
    T("ikon.svg sunucudan geliyor", ik["s"] == 200 and "<svg" in ik["t"], str(ik["s"]))

    # ---------- 2) ETKİNLİK ADI → KLASÖR · ETİKET · GALERİ · RAPOR ----------
    print("\n[2] Etkinlik adı zinciri (boş ad = bilinen risk)")
    def slug(ad): return pg.evaluate("(a)=>{B360.S.evt=a;B360.save();return B360.evSlug?B360.evSlug():B360.galeriUrl()}", ad)
    gal = lambda ad: pg.evaluate("(a)=>{B360.S.evt=a;B360.save();return B360.galeriUrl()}", ad)
    T("Türkçe ad sadeleşiyor (Şükrü & Gülşah Düğünü → sukru-gulsah-dugunu)",
      "t=sukru-gulsah-dugunu-360" in gal("Şükrü & Gülşah Düğünü"), gal("Şükrü & Gülşah Düğünü").split("#")[1][:60])
    T("ad BOŞKEN «etkinlik» klasörüne düşüyor (panele ad yazılmazsa iki iş karışır)",
      "t=etkinlik-360" in gal(""), gal("").split("#")[1][:40])
    T("yalnız sembolden oluşan ad da «etkinlik»e düşüyor", "t=etkinlik-360" in gal("!!! ***"), gal("!!! ***").split("#")[1][:40])
    uzun = "Uluslararası Kardiyovasküler Cerrahi Kongresi 2026 Gala Gecesi"
    et = gal(uzun).split("t=")[1].split("&")[0]
    T("çok uzun ad 40 karakterde kesiliyor", len(et) <= 44 and et.endswith("-360"), et)
    T("ad değişince etiket de değişiyor (ikinci iş ayrı galeriye düşer)",
      gal("Gala Gecesi") != gal("Kokteyl"), "gala≠kokteyl")
    pg.evaluate("B360.S.evt='Saha Testi 2';B360.save()")
    T("rapor adresi galeriyle AYNI etiketi taşıyor",
      "t=saha-testi-2-360" in ev("B360.raporUrl()") and "t=saha-testi-2-360" in ev("B360.galeriUrl()"),
      ev("B360.raporUrl()").split("#")[1][:52])

    # ---------- 3) İKİNCİ BOOTH'A AYAR AKTARIMI ----------
    print("\n[3] Ayar aktarımı — ikinci booth aynı kurulumu alsın, sayaç karışmasın")
    pg.evaluate("B360.S.sayac={'saha-testi-2':{cekim:7,teslim:7,gun:{}}};B360.S.bantAltMod='etkinlik';B360.save()")
    kod = ev("B360.ayarKod()")
    pak = json.loads(kod)
    T("ayar kodu geçerli JSON ve kurulumu taşıyor",
      pak.get("cldName") == "rqhgtbvd" and pak.get("bantAltMod") == "etkinlik", f"{len(kod)} karakter")
    T("SAYAÇ ayar paketine girmiyor (iki booth'un rakamı karışmaz)", "sayac" not in pak)
    T("cihaza özel kamera kaydı da taşınmıyor", "lastCam" not in pak and "camLog" not in pak)
    bag = ev("B360.ayarBag()")
    T("ayar bağlantısı #ayar= ile üretiliyor", "index.html#ayar=" in bag and len(bag) > 60, bag[:48] + "…")
    T("bağlantı base64 gövdesi geri çözülüyor",
      pg.evaluate("(b)=>{try{var s=b.split('#ayar=')[1].replace(/-/g,'+').replace(/_/g,'/');return JSON.parse(decodeURIComponent(escape(atob(s)))).cldName}catch(e){return 'HATA:'+e.message}}", bag) == "rqhgtbvd")
    yeni = json.dumps({"evt": "İkinci Booth", "cldName": "rqhgtbvd", "bantAltMod": "yok", "sayac": {"baska": {"cekim": 99}}})
    T("ayar uygulandı (hata dönmedi)", ev(f"B360.ayarUygula({json.dumps(yeni)})") == "")
    T("gelen ayar kuruldu", ev("B360.S.evt") == "İkinci Booth" and ev("B360.S.bantAltMod") == "yok")
    T("gelen ayar BU cihazın sayacını EZMEDİ",
      ev("JSON.stringify(B360.S.sayac['saha-testi-2']||{})").find('"cekim":7') > 0, ev("JSON.stringify(B360.S.sayac)")[:60])
    h1 = ev("B360.ayarUygula('bu bir ayar dosyası değil')")
    T("bozuk metin uygulanmıyor, Türkçe hata veriyor", h1.startswith("Okunamadı"), h1[:60])
    T("bozuk metin ayarları bozmuyor", ev("B360.S.cldName") == "rqhgtbvd")
    T("JSON ama ayar dosyası değilse ayrı uyarı", ev("B360.ayarUygula('123')") == "Metin ayar dosyası değil.",
      ev("B360.ayarUygula('123')"))
    pg.evaluate("B360.S.evt='Saha Testi 2';B360.save()")

    # ---------- 4) SAHA AYARLARI PANELDEN KAYDEDİLİYOR ----------
    print("\n[4] Saha ayarları — uyku · ses · oto-dön · ayna")
    pg.click("#gearBtn"); pg.wait_for_selector("#s-pin.on")
    for k in "1234": pg.click(f"#pinPad button:text-is('{k}')")
    pg.wait_for_selector("#s-admin.on")
    pg.select_option("#fWake", "0")
    T("ekran uyanık kalsın ayarı kaydediliyor", ev("B360.S.wake") == 0)
    pg.select_option("#fWake", "1"); T("uyku engelleme geri açılıyor", ev("B360.S.wake") == 1)
    pg.select_option("#fSesli", "0"); T("sesli uyarı kapatılabiliyor", ev("B360.S.sesli") == 0)
    pg.select_option("#fSesli", "1")
    pg.fill("#fOto", "45"); pg.dispatch_event("#fOto", "change")
    T("otomatik başa dönüş süresi kaydediliyor", ev("B360.S.otoDon") == 45, str(ev("B360.S.otoDon")))
    pg.fill("#fOto", "9999"); pg.dispatch_event("#fOto", "change")
    T("oto-dön üst sınırı 600 sn", ev("B360.S.otoDon") == 600, str(ev("B360.S.otoDon")))
    pg.fill("#fOto", "0"); pg.dispatch_event("#fOto", "change")
    pg.select_option("#fAyna", "1"); T("ayna ayarı kaydediliyor", ev("B360.S.ayna") == 1)
    pg.select_option("#fAyna", "0")
    T("tanı bilgisi saha için ekran/meşgul/kuyruk durumunu veriyor",
      set(["ekran", "mesgul", "bekleyen", "oto", "deneme"]).issubset(set(ev("Object.keys(B360.tani())"))),
      ", ".join(ev("Object.keys(B360.tani())"))[:60])

    # ---------- 5) DENEME MODU — kurulum çekimi sayaca ve müşteri klasörüne girmesin ----------
    print("\n[5] Deneme modu")
    pg.evaluate("B360.S.sayac={};B360.save()")
    pg.check("#fkDeneme")
    T("deneme modu açıldı", ev("B360.S.deneme") == 1)
    T("ekranda deneme uyarısı var", (pg.text_content("#denemeNot") or "").strip() != "",
      (pg.text_content("#denemeNot") or "").strip()[:60])
    pg.click("#s-admin .iconbtn"); pg.wait_for_selector("#s-attract.on")
    n0 = len(uploads["folder"])
    pg.click("#startBtn"); pg.wait_for_selector("#s-done.on", timeout=45000)
    T("deneme çekimi _deneme klasörüne gidiyor", uploads["folder"][n0:] == ["booth360/_deneme"], str(uploads["folder"][n0:]))
    T("deneme çekimi 'deneme-360' etiketiyle yükleniyor", uploads["tags"][-1] == "deneme-360", str(uploads["tags"][-1:]))
    T("deneme çekimi SAYACA girmiyor", ev("JSON.stringify(B360.S.sayac)") == "{}", ev("JSON.stringify(B360.S.sayac)")[:60])
    son = ev("B360.last()")          # başa dönünce KVKK temizliği adresi siler — burada al
    T("bitti ekranında misafir adresi hazır", bool(son.get("page")), (son.get("page") or "")[:60])
    pg.click("#againBtn"); pg.wait_for_selector("#s-attract.on")
    T("başa dönünce önceki misafirin adresi siliniyor (KVKK)", not (ev("B360.last()") or {}).get("page"))
    pg.evaluate("B360.S.deneme=0;B360.save()")

    # ---------- 6) MİSAFİR SAYFASI (v.html) ----------
    print("\n[6] Misafir sayfası")
    vp = ctx.new_page(); verrs = []
    vp.on("pageerror", lambda e: verrs.append(str(e)))
    vp.goto(son["page"]); vp.wait_for_function("!document.querySelector('#saveBtn').disabled", timeout=30000)
    T("karekoddaki sayfa açılıyor ve video hazır", vp.evaluate("!!document.querySelector('#vid').src"))
    T("kaydet düğmesi etkin", vp.evaluate("!document.querySelector('#saveBtn').disabled"))
    T("paylaş düğmesi var", vp.evaluate("!!document.querySelector('#shareBtn')"))
    T("misafir sayfası aynı videoyu gösteriyor",
      vp.evaluate("document.querySelector('#vid').src") == son["url"], vp.evaluate("document.querySelector('#vid').src")[-40:])
    T("misafir sayfasında JS hatası yok", not verrs, "; ".join(verrs)[:90])
    vp.close()

    # ---------- 7) MÜŞTERİ RAPORU (r.html) ----------
    print("\n[7] Müşteri raporu")
    rp = ctx.new_page(); rerrs = []
    rp.on("pageerror", lambda e: rerrs.append(str(e)))
    rp.goto(ev("B360.raporUrl()")); rp.wait_for_selector("#baslik")
    time.sleep(1.2)
    T("rapor başlığında etkinlik adı var", "Saha Testi 2" in (rp.text_content("#baslik") or ""), (rp.text_content("#baslik") or "")[:50])
    T("rapor buluttan video sayısını okuyor", "3" in (rp.text_content("#oSayi") or ""), (rp.text_content("#oSayi") or "")[:20])
    T("raporda galeri bağlantısı var", rp.evaluate("!!document.querySelector('#galeriBtn')"))
    T("raporda yazdır/PDF düğmesi var", rp.evaluate("!!document.querySelector('#yazdir')"))
    T("raporda JS hatası yok", not rerrs, "; ".join(rerrs)[:90])
    rp.close()

    # ---------- 8) SAYAÇ METNİ VE BAYAT AD UYARISI ----------
    print("\n[8] Sayaç metni · bayat ad uyarısı")
    pg.evaluate("B360.S.evt='Saha Testi 2';B360.save()")
    pg.evaluate("new Promise(function(r){B360.bulutSayim(function(){r(1)})})")
    sm = ev("B360.sayacMetin()")
    T("sayaç metni tüm booth'ların toplamını yazıyor", "TÜM BOOTH'LAR: 3" in sm, sm[:70])
    T("sayaç metni bu telefonun rakamını ayrı yazıyor", "Bu telefon:" in sm, sm[sm.find("Bu telefon:"):][:40])
    by = ev("B360.bayatAd()")
    T("dünden kalan ad için 'adı değiştir' uyarısı çıkıyor", "etkinlik adını değiştir" in by, by[:80])
    T("uyarı iki işin aynı galeriye düşeceğini söylüyor", "aynı galeriye" in by, by[-60:])
    liste["zaman"] = BUGUN
    pg.evaluate("new Promise(function(r){B360.bulutSayim(function(){r(1)})})")
    T("bugünkü işte bayat ad uyarısı çıkmıyor", ev("B360.bayatAd()") == "", ev("B360.bayatAd()")[:40])

    print("\n[9] Sayfa sağlığı")
    T("booth ekranında JS hatası yok", not errs, "; ".join(errs)[:120])
    br.close()

print(f"\nSONUÇ: {ok}/{ok+bad} geçti" + (" — HATALAR: " + ", ".join(dusen) if dusen else ""))
sys.exit(0 if bad == 0 else 1)
