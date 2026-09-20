#!/usr/bin/env python3
"""OBSKURA 360 — DÜZ BANT YAZISI takımı (20 Eyl 2026'da yeniden yazıldı).
   Kapsam: bant geometrisi (düzen · kalınlık · zemin), yazı katmanı (punto, renk,
   font, dikey ortalama, ÇİFT encode), katman önceliği, panel uyarıları ve isimli renkler.
   Şerit görseli → t360bantgorsel · iki logo + 3 satır → t360bantparca."""
import sys, time, threading, http.server, socketserver, pathlib, functools, json
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8406; BASE = f"http://localhost:{PORT}/"

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

INIT = {"evt": "Kardiyovasküler Kongresi 2026", "cldName": "rqhgtbvd", "cldPreset": "booth_qr",
        "paket": "editsiz", "mod": "editsiz", "logoPid": "", "logoZorunlu": 0,
        "bantAltMod": "yok", "bantUstMod": "yok", "bantYer": "ikisi", "bantYuk": 170,
        "bantBoy": 46, "bantRenk": "F3EDE4", "bantFont": "Montserrat", "bantZemin": "0D0B0A",
        "bantKaydir": 0, "direkt": 1}

with sync_playwright() as p:
    br = p.chromium.launch(args=["--no-sandbox"])
    ctx = br.new_context(viewport={"width": 430, "height": 932})
    ctx.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    ctx.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    ctx.route("**/*cloudinary.com/**", lambda r: r.fulfill(status=200, body=""))
    ctx.add_init_script("try{localStorage.setItem('booth360.v1',JSON.stringify(" + json.dumps(INIT) + "))}catch(e){}")
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "index.html"); pg.wait_for_selector("#s-attract.on")
    def ev(js): return pg.evaluate(js)
    print("sürüm:", ev("B360.VER"))

    # ---------- 1) BANT GEOMETRİSİ: düzen, kalınlık, zemin ----------
    print("\n[1] Bant geometrisi — düzen · kalınlık · zemin")
    def kad(bp, bh, bb="0D0B0A"):
        return ev(f"B360E.kadraj('g916d',{{bp:'{bp}',bh:{bh},bb:'{bb}'}})")
    T("düzen 'ikisi' · 170 px → içerik 1080×1580, alt+üst bant",
      kad("ikisi", 170) == "c_fill,w_1080,h_1580,g_center/c_pad,w_1080,h_1920,b_rgb:0D0B0A", kad("ikisi", 170))
    T("düzen 'alt' → tek bant (1750) ve içerik yukarı yaslı (g_north)",
      kad("alt", 170) == "c_fill,w_1080,h_1750,g_center/c_pad,w_1080,h_1920,g_north,b_rgb:0D0B0A", kad("alt", 170))
    T("düzen 'ust' → içerik aşağı yaslı (g_south)", ",g_south," in kad("ust", 170), kad("ust", 170))
    T("düzen 'yok' → bant yok, tam ekran kırpar",
      kad("yok", 170) == "c_fill,w_1080,h_1920,g_center", kad("yok", 170))
    T("kalınlık 240 → içerik 1440 (3:4, en geniş kadraj)", "h_1440,g_center" in kad("ikisi", 240), kad("ikisi", 240))
    T("kalınlık 120 → içerik 1680", "h_1680,g_center" in kad("ikisi", 120), kad("ikisi", 120))
    T("kalınlık 0 → bant yok sayılır", kad("ikisi", 0) == "c_fill,w_1080,h_1920,g_center", kad("ikisi", 0))
    T("kalınlık üst sınırı 400 px (500 istense de)", kad("ikisi", 500) == kad("ikisi", 400), kad("ikisi", 500))
    T("bant zemini panelden gelen renk", "b_rgb:1A2B3C" in kad("ikisi", 170, "1A2B3C"), kad("ikisi", 170, "1A2B3C"))
    T("bant zemini 'blur' seçilince bulanık", "b_blurred:400:15" in kad("ikisi", 170, "blur"), kad("ikisi", 170, "blur"))
    T("zemin kodundaki geçersiz karakterler temizlenir", "b_rgb:F2A93B" in kad("ikisi", 170, "#F2A93B!"), kad("ikisi", 170, "#F2A93B!"))

    # ---------- 2) YAZI KATMANI ----------
    print("\n[2] Yazı katmanı — punto · renk · font · konum")
    def kat(metin, spec, yon="alt"):
        return ev(f"B360E.bantKat({json.dumps(metin)},{spec},'{yon}').join('/')")
    a = kat("YOPI EVENTS", "{bh:240,bp:'ikisi',bs:46,bc:'F3EDE4',bf:'Montserrat'}")
    T("alt yazı bandın altına oturuyor (g_south)", "fl_layer_apply,g_south,y_" in a, a[-40:])
    T("yazı 940 px'e sığdırılıyor (uzun ad kesilmez, sarar)", "c_fit,w_940" in a, a[:70])
    T("satırlar ortalı basılıyor (_bold_center)", "_46_bold_center:" in a, a[:50])
    u = kat("YOPI EVENTS", "{bh:240,bp:'ikisi',bs:46}", "ust")
    T("üst yazı bandın üstüne oturuyor (g_north)", "fl_layer_apply,g_north,y_" in u, u[-40:])
    T("yazı banda dikey ORTALANIYOR (240 px bant, 46 punto → y_104)", a.endswith("y_104"), a[-12:])
    k2 = kat("X", "{bh:120,bp:'ikisi',bs:100}")
    T("punto büyüyünce ortalama yeniden hesaplanıyor (120 px bant, 100 punto → y_24)", k2.endswith("y_24"), k2[-12:])
    k3 = kat("X", "{bh:120,bp:'ikisi',bs:100,bo:10}")
    T("ince ayar (kaydır) yazıyı oynatıyor (+10 → y_34)", k3.endswith("y_34"), k3[-12:])
    k4 = kat("X", "{bp:'yok',bh:0,by:92,bs:46}")
    T("bantsız düzende yazı görüntünün üstünde, kenardan y_92", k4.endswith("y_92"), k4[-12:])
    T("punto alt sınırı 18", "_18_bold_center:" in kat("X", "{bh:240,bp:'ikisi',bs:5}"))
    T("punto üst sınırı 120", "_120_bold_center:" in kat("X", "{bh:240,bp:'ikisi',bs:500}"))
    T("renk kodu temizleniyor (#F2A93B → F2A93B)", "co_rgb:F2A93B" in kat("X", "{bh:240,bp:'ikisi',bc:'#F2A93B'}"))
    T("geçersiz renk → varsayılan F3EDE4", "co_rgb:F3EDE4" in kat("X", "{bh:240,bp:'ikisi',bc:'zzz'}"))
    T("iki kelimelik yazı tipi (Playfair Display → %20)",
      "l_text:Playfair%20Display_" in kat("X", "{bh:240,bp:'ikisi',bf:'Playfair Display'}"))
    T("yazı tipi adındaki özel karakterler atılıyor",
      "l_text:Montserratx_" in kat("X", "{bh:240,bp:'ikisi',bf:'Mont!serrat;x'}"))
    T("boş metin → katman yok", ev("B360E.bantKat('   ',{bh:240,bp:'ikisi'},'alt').length") == 0)

    # ---------- 3) METİN ENCODE (karekod ve URL bozulmasın) ----------
    print("\n[3] Metin encode — Türkçe · virgül · eğik çizgi")
    T("Türkçe harfler doğru encode ediliyor", ev("B360E.txtEnc('Şükrü & Gülşah')") == "%C5%9Ekr%C3%BC%20%26%20G%C3%BCl%C5%9Fah".replace("%C5%9Ekr", "%C5%9E%C3%BCkr"),
      ev("B360E.txtEnc('Şükrü & Gülşah')"))
    T("virgül ÇİFT encode (%252C) — URL yapısı bozulmuyor", ev("B360E.txtEnc('Ankara, 2026')") == "Ankara%252C%202026",
      ev("B360E.txtEnc('Ankara, 2026')"))
    T("eğik çizgi ÇİFT encode (%252F)", ev("B360E.txtEnc('A/B')") == "A%252FB", ev("B360E.txtEnc('A/B')"))
    T("baştaki/sondaki boşluk kırpılıyor", ev("B360E.txtEnc('  YOPI  ')") == "YOPI")

    # ---------- 4) KATMAN ÖNCELİĞİ ----------
    print("\n[4] Katman önceliği — görsel > parçalı içerik > düz yazı")
    BAZ = "{c:'rqhgtbvd',p:'booth360/deneme/abc',v:1,t:'ham',bh:240,bp:'ikisi',bb:'0D0B0A',bs:46}"
    u_yazi = ev(f"B360E.url(Object.assign({BAZ},{{ba:'DUZYAZI'}}))")
    T("düz yazı tek başına basılıyor", "l_text:" in u_yazi and "DUZYAZI" in u_yazi, u_yazi.split("/upload/")[1][:60])
    u_gor = ev(f"B360E.url(Object.assign({BAZ},{{ba:'DUZYAZI',bga:'booth360/_bant/serit'}}))")
    T("aynı yönde şerit görseli varsa düz yazı BASILMIYOR", "DUZYAZI" not in u_gor and "l_booth360:_bant:serit" in u_gor,
      u_gor.split("/upload/")[1][:60])
    u_par = ev(f"B360E.url(Object.assign({BAZ},{{ba:'DUZYAZI',b1:'SATIR1'}}))")
    T("parçalı içerik varsa düz yazı BASILMIYOR", "DUZYAZI" not in u_par and "SATIR1" in u_par, u_par.split("/upload/")[1][:60])
    u_alt = ev(f"B360E.url(Object.assign({BAZ},{{bp:'alt',bu:'USTYAZI',ba:'ALTYAZI'}}))")
    T("düzen 'sadece alt' → ÜST yazı videoya girmiyor", "USTYAZI" not in u_alt and "ALTYAZI" in u_alt)
    u_kapali = ev(f"B360E.url(Object.assign({BAZ},{{ba:'DUZYAZI',o:{{bant:0}}}}))")
    T("bant bayrağı kapalı → ham video HİÇ işlenmiyor (0 kredi)",
      "/video/upload/v1/booth360/deneme/abc.mp4" in u_kapali, u_kapali[-46:])
    T("bantVar(): yazı varken doğru, yokken yanlış",
      ev(f"B360E.bantVar(Object.assign({BAZ},{{ba:'X'}}))") is True and ev(f"B360E.bantVar({BAZ})") is False)

    # ---------- 5) PANEL: metin kaynağı ve alan görünürlüğü ----------
    print("\n[5] Panel — metin kaynağı · alanlar")
    pg.click("#gearBtn"); pg.wait_for_selector("#s-pin.on")
    for k in "1234": pg.click(f"#pinPad button:text-is('{k}')")
    pg.wait_for_selector("#s-admin.on")
    pg.evaluate("B360.S.bantAltMod='etkinlik';B360.save()")
    T("mod 'etkinlik' → alt banda etkinlik adı gider", ev("B360.bantMetin('alt')") == INIT["evt"], ev("B360.bantMetin('alt')"))
    pg.select_option("#fBantAltMod", "ozel")
    pg.fill("#fBantAltTxt", "YOPI EVENTS")
    T("panelden 'özel' seçilince metin satırı açılıyor", ev("document.querySelector('#fBantAltTxtRow').hidden") is False)
    T("özel metin ayarlara yazıldı", ev("B360.S.bantAltTxt") == "YOPI EVENTS" and ev("B360.bantMetin('alt')") == "YOPI EVENTS")
    pg.select_option("#fBantAltMod", "yok")
    T("mod 'yok' → yazı kapalı", ev("B360.bantMetin('alt')") == "")
    T("mod 'yok' seçilince metin satırı gizleniyor", ev("document.querySelector('#fBantAltTxtRow').hidden") is True)

    # ---------- 6) PANEL: taşma ve düzen uyarıları ----------
    print("\n[6] Panel — taşma ve düzen uyarıları")
    pg.evaluate("B360.S.bantBoy=46;B360.S.bantYuk=170;B360.S.bantYer='ikisi';B360.save()")
    T("kısa yazı + orta punto → uyarı yok", ev("B360.tasmaUyari('YOPI')") == "", ev("B360.tasmaUyari('YOPI')"))
    T("uzun kongre adı 46 puntoda 170 px banda sığıyor → uyarı yok (canlıda ölçüldü)",
      ev("B360.tasmaUyari('Kardiyovasküler Kongresi 2026')") == "", ev("B360.tasmaUyari('Kardiyovasküler Kongresi 2026')")[:60])
    pg.evaluate("B360.S.bantBoy=70;B360.save()")
    uz = ev("B360.tasmaUyari('Kardiyovasküler Kongresi 2026')")
    T("aynı ad 70 puntoda taşıyor → uyarı", "sığmaz" in uz, uz[:70])
    T("uyarı çözüm söylüyor (kısalt / puntoyu küçült / bandı kalınlaştır)",
      ("kısalt" in uz or "puntoyu küçült" in uz or "kalınlaştır" in uz), uz[-60:])
    pg.evaluate("B360.S.bantBoy=110;B360.S.bantYuk=120;B360.save()")
    T("ince bantta büyük punto kısa yazıda bile taşıyor", "sığmaz" in ev("B360.tasmaUyari('YOPI')"),
      ev("B360.tasmaUyari('YOPI')")[:60])
    pg.evaluate("B360.S.bantBoy=58;B360.S.bantYuk=240;B360.save()")
    sar = ev("B360.tasmaUyari('Uluslararası Kardiyoloji Kongresi 26')")
    T("banda sığan ama iki satıra saran yazı için ayrı uyarı", "iki satıra sarar" in sar, sar[:70])
    T("uyarı somut yazı boyu öneriyor", "Yazı boyunu «Orta» yap" in sar, sar[-40:])
    pg.evaluate("B360.S.bantBoy=46;B360.S.bantYuk=170;B360.save()")
    pg.evaluate("B360.S.bantBoy=46;B360.S.bantYer='alt';B360.S.bantUstMod='ozel';B360.S.bantUstTxt='USTYAZI';B360.save()")
    pg.select_option("#fBantYer", "alt")
    not_metni = ev("document.querySelector('#bantNot').textContent")
    T("düzen 'sadece alt' iken ÜST yazı için panelde uyarı var", "ÜST yazı videoda çıkmaz" in not_metni, not_metni[:90])
    pg.evaluate("B360.S.bantUstMod='yok';B360.S.bantAltMod='yok';B360.save()")
    pg.select_option("#fBantYer", "ikisi")
    T("yazı kapalıyken panel 'videoda yazı çıkmaz' diyor",
      "Bant yazısı kapalı" in ev("document.querySelector('#bantNot').textContent"),
      ev("document.querySelector('#bantNot').textContent")[:80])

    # ---------- 7) İSİMLİ RENKLER (saha ekibi kod yazmasın) ----------
    print("\n[7] İsimli renkler")
    T("hazır renk paleti duruyor", ev("B360.BANT_RENKLER.length") == 9, str(ev("B360.BANT_RENKLER")))
    pg.evaluate("B360.S.bantRenk='F2A93B';B360.bantRenkYaz()")
    T("hazır renk seçiliyken kod kutusu gizli",
      ev("document.querySelector('#fBantRenk').hidden") is True and ev("document.querySelector('#fBantRenkSec').value") == "F2A93B")
    pg.evaluate("B360.S.bantRenk='123456';B360.bantRenkYaz()")
    T("palet dışı renk → 'özel' görünür, kod kutusu açık",
      ev("document.querySelector('#fBantRenkSec').value") == "ozel" and ev("document.querySelector('#fBantRenk').hidden") is False)
    pg.evaluate("B360.S.bantRenk='F3EDE4';B360.bantRenkYaz()")

    # ---------- 8) UÇTAN UCA: panel ayarı videoya gidiyor mu ----------
    print("\n[8] Uçtan uca — panel → video adresi")
    pg.evaluate("""B360.S.bantAltMod='etkinlik';B360.S.bantYer='ikisi';B360.S.bantYuk=240;
                   B360.S.bantBoy=46;B360.S.bantRenk='F2A93B';B360.S.bantFont='Montserrat';B360.save();
                   B360.setVid({pid:'booth360/deneme/abc123',ver:1725500000,dur:15.2})""")
    son = ev("B360.tplUrl('ham')")
    T("panelde açılan bant yazısı ham videoya basılıyor", "l_text:Montserrat_46_bold_center:" in son, son.split("/upload/")[1][:60])
    T("etkinlik adı Türkçe karakterleriyle doğru gidiyor", "Kardiyovask%C3%BCler" in son, son[son.find("l_text"):][:60])
    T("panelden seçilen renk videoya gidiyor", "co_rgb:F2A93B" in son)
    T("240 px bant geometrisi videoya gidiyor", "c_fill,w_1080,h_1440,g_center" in son)
    pg.evaluate("B360.S.bantAltMod='yok';B360.save()")
    T("yazı kapatılınca ham video hiç işlenmiyor (0 kredi)",
      "/video/upload/v1725500000/" in ev("B360.tplUrl('ham')"), ev("B360.tplUrl('ham')")[-52:])

    print("\n[9] Sayfa sağlığı")
    T("JS hatası yok", not errs, "; ".join(errs)[:120])
    br.close()

print(f"\nSONUÇ: {ok}/{ok+bad} geçti" + (" — HATALAR: " + ", ".join(dusen) if dusen else ""))
sys.exit(0 if bad == 0 else 1)
