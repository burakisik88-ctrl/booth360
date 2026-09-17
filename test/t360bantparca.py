#!/usr/bin/env python3
"""OBSKURA 360 — BANT İÇERİĞİ (iki logo + 3 satır) testi (17 Eyl 2026).
   Burak: "sen 2 logo yükleyebilmeyi çöz, iki tane logoyu ayrı ayrı yükleyelim,
           sonra normal yazı yazalım — yazı 3 satır şeklinde yazılabilir olmalı ki
           iki logonun arasına girebilsin." """
import sys,time,threading,http.server,socketserver,pathlib,functools
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path("/home/claude/booth360"); PORT=8404; BASE=f"http://localhost:{PORT}/"
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address=True
    with socketserver.TCPServer(("127.0.0.1",PORT),functools.partial(Q,directory=str(ROOT))) as h: h.serve_forever()
threading.Thread(target=serve,daemon=True).start(); time.sleep(0.4)
ok=0;bad=0
def T(n,c,e=""):
    global ok,bad
    if c: ok+=1; print(f"  ok   {n}")
    else: bad+=1; print(f"  FAIL {n} -> {e}")

with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox","--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream","--autoplay-policy=no-user-gesture-required"])
    ctx=b.new_context(viewport={"width":430,"height":932},permissions=["camera"])
    def cld(r):
        if "/upload" in r.request.url and r.request.method=="POST":
            r.fulfill(status=200,content_type="application/json",
                      body='{"public_id":"booth360/_bant/deneme","version":1}')
        else: r.fulfill(status=200,body="")
    ctx.route("**/*cloudinary.com/**", cld)
    ctx.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    ctx.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    pg=ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"index.html"); pg.wait_for_selector("#s-attract.on")

    TAM = ("{c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF',"
           "bl:'booth360/_bant/sol',br:'booth360/_bant/sag',blw:250,brw:200,"
           "b1:'BIR',b2:'IKI',b3:'UC',c1:'E5484D',c2:'12100E',c3:'E5484D',bs:46,bf:'Montserrat'}")

    print("\n[1] İki logo ayrı ayrı basılıyor")
    r=pg.evaluate("()=>B360E.chain(%s)"%TAM)
    T("sol logo sola yapışık", "l_booth360:_bant:sol/c_fit,w_250,h_216/c_pad,w_250,h_240,b_transparent/fl_layer_apply,g_south_west,x_24" in r, r)
    T("sağ logo sağa yapışık", "l_booth360:_bant:sag/c_fit,w_200,h_216/c_pad,w_200,h_240,b_transparent/fl_layer_apply,g_south_east,x_24" in r, r)
    T("logolar bant ölçüsünde kutuya ortalanıyor (taşmaz)", r.count("c_pad,w_")>=2, r)

    print("\n[2] Üç satır ayrı ayrı, kendi renkleriyle")
    T("1. satır kırmızı", "l_text:Montserrat_46_bold_center:BIR,co_rgb:E5484D" in r, r)
    T("2. satır siyah", "l_text:Montserrat_46_bold_center:IKI,co_rgb:12100E" in r, r)
    T("3. satır kırmızı", "l_text:Montserrat_46_bold_center:UC,co_rgb:E5484D" in r, r)

    print("\n[3] Satırlar bandın içinde, üstten alta doğru sıralı")
    import re
    ys=[int(m) for m in re.findall(r"fl_layer_apply,g_south,x_-?\d+,y_(\d+)", r)]
    T("üç satırın da y'si var", len(ys)==3, ys)
    T("1. satır en üstte (y en büyük)", ys==sorted(ys,reverse=True), ys)
    T("hepsi 240 px bandın içinde", all(0<=y<=240 for y in ys), ys)
    T("satır aralığı eşit", len(set([ys[0]-ys[1],ys[1]-ys[2]]))==1, ys)

    print("\n[4] Yazı İKİ LOGONUN ARASINA ortalanıyor")
    dx=re.findall(r"fl_layer_apply,g_south,x_(-?\d+),y_", r)
    # sol 250 + ara 18, sag 200 + ara 18 -> merkez saga kayar
    T("x kayması sağa (sol logo daha geniş)", int(dx[0])==25, dx)
    gen=re.findall(r"c_fit,w_(\d+)\n?", r.replace("/","\n"))
    T("yazı alanı logolar arasındaki boşluk (546 px)", "c_fit,w_546" in r, r)

    print("\n[5] Tek logo / eksik satır bozmuyor")
    r2=pg.evaluate("()=>B360E.chain({c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF',bl:'booth360/_bant/sol',blw:250,b1:'TEK',bs:46})")
    T("sadece sol logo + tek satır çalışıyor", "g_south_west" in r2 and "l_text" in r2 and "g_south_east" not in r2, r2)
    r3=pg.evaluate("()=>B360E.chain({c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF',b1:'A',b3:'C',bs:46})")
    T("2. satır boşken 1 ve 3 ortalanıyor", r3.count("l_text")==2, r3)
    r4=pg.evaluate("()=>B360E.chain({c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF',bl:'booth360/_bant/sol',br:'booth360/_bant/sag',blw:250,brw:250})")
    T("yazısız iki logo çalışıyor", "g_south_west" in r4 and "g_south_east" in r4 and "l_text" not in r4, r4)

    print("\n[6] Punto banda sığmıyorsa küçültülüyor")
    r5=pg.evaluate("()=>B360E.chain({c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF',b1:'A',b2:'B',b3:'C',bs:70})")
    T("70 punto 3 satır 240'a sığmaz → küçültülüyor", "_70_bold_center" not in r5, r5)
    ys5=[int(m) for m in re.findall(r"y_(\d+)", r5)]
    T("küçültülen satırlar hâlâ bandın içinde", all(0<=y<=240 for y in ys5), ys5)

    print("\n[7] Öncelik sırası: şerit görseli > parçalı > düz yazı")
    r6=pg.evaluate("()=>B360E.chain({c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF',bga:'booth360/_bant/serit',bl:'booth360/_bant/sol',b1:'X',ba:'DUZ',bs:46})")
    T("şerit görseli varsa o basılır", "_bant:serit/c_fill,w_1080,h_240" in r6, r6)
    T("şerit varken parçalı basılmaz", "g_south_west" not in r6, r6)
    r7=pg.evaluate("()=>B360E.chain({c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF',bl:'booth360/_bant/sol',b1:'X',ba:'DUZ',bs:46})")
    T("parçalı varken düz bant yazısı basılmaz", "DUZ" not in r7, r7)
    T("parçalı içerik basılıyor", "l_text:Montserrat_46_bold_center:X" in r7, r7)

    print("\n[8] Üst bantta sıralama ters (üstten ölçülüyor)")
    r8=pg.evaluate("()=>B360E.chain({c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'ust',bb:'FFFFFF',b1:'A',b2:'B',b3:'C',bs:46})")
    ys8=[int(m) for m in re.findall(r"g_north,y_(\d+)", r8)]
    T("üst bantta 1. satır en üstte (y en küçük)", ys8==sorted(ys8), ys8)
    T("üst bant g_north kullanıyor", "g_north" in r8, r8)

    print("\n[9] Ham videoda da basılıyor (bulut işlemi tetikleniyor)")
    r9=pg.evaluate("()=>B360E.url({c:'rqhgtbvd',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF',bl:'booth360/_bant/sol',blw:250,b1:'X',bs:46})")
    T("ham adres parçalı katmanı içeriyor", "_bant:sol" in r9 and "l_text" in r9, r9)

    print("\n[10] Panel: alanlar ve önizleme")
    pg.click("#gearBtn"); pg.wait_for_timeout(250)
    for d in "1234": pg.click(f"#pinPad button:has-text('{d}')",timeout=2000)
    pg.wait_for_timeout(400)
    for sel,ad in [("#blBtn","SOL logo yükle"),("#brBtn","SAĞ logo yükle"),
                   ("#fBs1","1. satır"),("#fBs2","2. satır"),("#fBs3","3. satır"),
                   ("#fBc1","1. satır rengi"),("#fBlW","sol logo genişliği")]:
        T(ad+" alanı var", pg.locator(sel).count()==1)
    r10=pg.evaluate("""()=>{
      B360.S.bantS1="BIR";B360.S.bantS2="IKI";B360.S.bantS3="UC";
      B360.S.bantC1="E5484D";B360.S.bantYer="alt";B360.save();
      const a=B360.bantAlan();
      return {b1:a.b1,b2:a.b2,b3:a.b3,c1:a.c1,bh:a.bh,bp:a.bp}}""")
    T("panel değerleri spec'e geçiyor", r10.get("b1")=="BIR" and r10.get("b3")=="UC", r10)
    T("parçalı içerik bant kalınlığını 240 yapıyor", r10.get("bh")==240, r10)
    r11=pg.evaluate("""()=>{B360.onizleYaz();
      const k=document.querySelector("#bantOnizle .bo-alt .bo-parca");
      return {gorunur:k&&k.style.display==="flex", satir:k?k.querySelectorAll("b i").length:0}}""")
    T("önizlemede parçalı bant görünüyor", r11.get("gorunur")==True, r11)
    T("önizlemede 3 satır çizilmiş", r11.get("satir")==3, r11)

    print("\n[11] Uyarılar")
    r12=pg.evaluate("""()=>{B360.S.bantBoy=70;B360.save();B360.parcaYaz&&B360.parcaYaz();
      return document.querySelector("#parcaNot").textContent}""")
    T("sığmayan punto uyarısı çıkıyor", "sığmıyor" in (r12 or ""), r12)

    print("\n[12] Sayfa hatası yok")
    T("JS hatası yok", not errs, errs)
    b.close()

print(f"\nSONUÇ: {ok}/{ok+bad} geçti")
sys.exit(0 if bad==0 else 1)
