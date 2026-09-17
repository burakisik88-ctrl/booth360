#!/usr/bin/env python3
"""OBSKURA 360 — BANT GÖRSELİ + BANT İÇİ LOGO testi (17 Eyl 2026).
   Burak: "bu tasarımı bizim alt banta denk gelecek şekilde tasarlayabilir misin"
          "bandın tamamına denk gelecek şekilde ölçüsü olmalı, tasarımcıya verebileyim"
          "logo oturma alanına işlem yapmak lazım, bana max boyut ver" """
import sys,time,threading,http.server,socketserver,pathlib,functools
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path("/home/claude/booth360"); PORT=8402; BASE=f"http://localhost:{PORT}/"
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
                      body='{"public_id":"booth360/_logo/deneme","version":1}')
        else:
            r.fulfill(status=200,body="")
    ctx.route("**/*cloudinary.com/**", cld)
    ctx.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    ctx.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    pg=ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"index.html"); pg.wait_for_selector("#s-attract.on")

    BAZ="{c:'c',p:'booth360/x',v:1,t:'ham',bh:240,bp:'alt',bb:'FFFFFF'}"

    print("\n[1] Bant görseli bandın TAMAMINI kaplıyor mu")
    r=pg.evaluate("()=>{const E=B360E;const u=E.chain(Object.assign(%s,{bga:'booth360/_bant/k'}));return u}"%BAZ)
    T("görsel katmanı var", "l_booth360:_bant:k" in r, r)
    T("bant ölçüsüne birebir (c_fill,w_1080,h_240)", "c_fill,w_1080,h_240" in r, r)
    T("alta yapışık (g_south)", "fl_layer_apply,g_south" in r, r)
    T("kenar boşluğu YOK (y_ ofseti yok)", "g_south,y_" not in r, r)

    print("\n[2] Görsel varken o bandın YAZISI basılmıyor")
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{bga:'booth360/_bant/k',ba:'YAZI'}))}"%BAZ)
    T("l_text basılmadı", "l_text" not in r, r)
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{ba:'YAZI'}))}"%BAZ)
    T("görsel yokken yazı hâlâ basılıyor", "l_text" in r, r)

    print("\n[3] Üst ve alt ayrı ayrı çalışıyor")
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{bp:'ikisi',bgu:'booth360/_bant/u',bga:'booth360/_bant/a'}))}"%BAZ)
    T("üst görsel g_north", "l_booth360:_bant:u/c_fill,w_1080,h_240/fl_layer_apply,g_north" in r, r)
    T("alt görsel g_south", "l_booth360:_bant:a/c_fill,w_1080,h_240/fl_layer_apply,g_south" in r, r)
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{bp:'alt',bgu:'booth360/_bant/u'}))}"%BAZ)
    T("düzen 'sadece alt' iken ÜST görsel basılmaz", "_bant:u" not in r, r)

    print("\n[4] Bant görseli varken ham video bulut işleminden geçiyor")
    r=pg.evaluate("()=>{const E=B360E;return E.url(Object.assign(%s,{bga:'booth360/_bant/k'}))}"%BAZ)
    T("ham URL işlem zinciri içeriyor", "_bant:k" in r and "/upload/c_fill" in r, r)

    print("\n[5] LOGO — bandın içine ortalı")
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{l:'booth360/_logo/y',lp:'balt',lw:'0.22'}))}"%BAZ)
    T("logo kutusu bant iç yüksekliğine sığdırılıyor", "c_fit,w_238,h_212" in r, r)
    T("saydam kutuyla bant ölçüsüne ortalanıyor", "c_pad,w_238,h_240,b_transparent" in r, r)
    T("bandın üstüne birebir oturuyor", "fl_layer_apply,g_south" in r, r)
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{l:'booth360/_logo/y',lp:'bust',bp:'ust'}))}"%BAZ)
    T("üst bant içi g_north", "c_pad,w_238,h_240,b_transparent/fl_layer_apply,g_north" in r, r)
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{l:'booth360/_logo/y',lp:'balt',bp:'yok',bh:0}))}"%BAZ)
    T("bant yokken kenara düşüyor (çökmüyor)", "c_scale,w_0.22,fl_relative" in r and "g_south" in r, r)
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{l:'booth360/_logo/y',lp:'ne'}))}"%BAZ)
    T("eski köşe konumu bozulmadı", "c_scale,w_0.22,fl_relative/fl_layer_apply,g_north_east,x_0.04,y_0.03" in r, r)

    print("\n[5b] LOGO — bandı TAMAMEN kaplama (tek parça şerit)")
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{l:'booth360/_logo/serit',lp:'dalt'}))}"%BAZ)
    T("şerit bandı birebir dolduruyor", "l_booth360:_logo:serit/c_fill,w_1080,h_240/fl_layer_apply,g_south" in r, r)
    seg=r.split("l_booth360:_logo:serit/")[1].split("/fl_layer_apply")[0] if "l_booth360:_logo:serit/" in r else ""
    T("logo katmanında kırpma/kutulama yok — şerit tam oturuyor",
      seg=="c_fill,w_1080,h_240", seg)
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{l:'booth360/_logo/serit',lp:'dust',bp:'ust'}))}"%BAZ)
    T("üst bandı kaplama g_north", "c_fill,w_1080,h_240/fl_layer_apply,g_north" in r, r)
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{l:'booth360/_logo/serit',lp:'dalt',bp:'yok',bh:0}))}"%BAZ)
    T("bant yokken kenara düşüyor", "c_scale,w_0.22,fl_relative" in r, r)

    print("\n[6] Genişlik seçimi kutuya yansıyor")
    r=pg.evaluate("()=>{const E=B360E;return E.chain(Object.assign(%s,{l:'booth360/_logo/y',lp:'balt',lw:'0.30'}))}"%BAZ)
    T("Büyük = 324 px", "c_fit,w_324,h_212" in r, r)

    print("\n[7] Panel ayarı → URL yolculuğu")
    pg.click("#gearBtn"); pg.wait_for_timeout(250)
    for d in "1234": pg.click(f"#pinPad button:has-text('{d}')",timeout=2000)
    pg.wait_for_timeout(350)
    T("ALT bant görseli yükle düğmesi var", pg.locator("#bgaBtn").count()==1)
    T("ÜST bant görseli yükle düğmesi var", pg.locator("#bguBtn").count()==1)
    T("logo konumunda 'bandın içine' seçeneği var",
      pg.locator("#fLogoPoz option[value='balt']").count()==1)
    T("logo konumunda 'bandı tamamen kapla' seçeneği var",
      pg.locator("#fLogoPoz option[value='dalt']").count()==1)
    r=pg.evaluate("""()=>{B360.S.bantGorAlt='booth360/_bant/k';B360.S.bantYuk=120;B360.save();
        const a=B360.bantAlan?B360.bantAlan():null; return a}""")
    if r is None:
        r=pg.evaluate("""()=>{B360.S.bantGorAlt='booth360/_bant/k';B360.S.bantYuk=120;B360.save();
            return {bh:(typeof bantAlan==='function')?bantAlan().bh:null}}""")
    T("görsel yüklüyken kalınlık 240'a sabitleniyor", r and r.get("bh")==240, r)

    print("\n[7b] ŞERİT otomatik algılama (Burak sahada ayarı bulamadı)")
    r=pg.evaluate("""()=>{
      const B=B360;
      B.S.logoPid=""; B.S.logoPoz="s"; B.S.bantYer="yok"; B.S.bantYuk=170; B.save();
      /* 1080x240 serit taklidi */
      const c=document.createElement("canvas"); c.width=1080; c.height=240;
      const x=c.getContext("2d"); x.fillStyle="#fff"; x.fillRect(0,0,1080,240);
      return new Promise(ok=>c.toBlob(b=>{
        const f=new File([b],"serit.png",{type:"image/png"});
        const dt=new DataTransfer(); dt.items.add(f);
        const inp=document.querySelector("#logoFile");
        inp.files=dt.files; inp.dispatchEvent(new Event("change",{bubbles:true}));
        setTimeout(()=>ok({poz:B.S.logoPoz,yer:B.S.bantYer,yuk:B.S.bantYuk,pid:B.S.logoPid}),2500);
      },"image/png"));
    }""")
    T("şerit yüklenince konum kendiliğinden 'bandı kapla' oluyor", r.get("poz")=="dalt", r)
    T("bant düzeni 'alt'a çekiliyor", r.get("yer")=="alt", r)
    T("bant kalınlığı 240'a çekiliyor", r.get("yuk")==240, r)
    r=pg.evaluate("""()=>{
      const B=B360; B.S.logoPid=""; B.S.logoPoz="ne"; B.save();
      const c=document.createElement("canvas"); c.width=400; c.height=400;
      const x=c.getContext("2d"); x.fillStyle="#fff"; x.fillRect(0,0,400,400);
      return new Promise(ok=>c.toBlob(b=>{
        const f=new File([b],"kare.png",{type:"image/png"});
        const dt=new DataTransfer(); dt.items.add(f);
        const inp=document.querySelector("#logoFile");
        inp.files=dt.files; inp.dispatchEvent(new Event("change",{bubbles:true}));
        setTimeout(()=>ok({poz:B.S.logoPoz,pid:B.S.logoPid}),2500);
      },"image/png"));
    }""")
    T("normal (kare) logoda konum DEĞİŞMİYOR", r.get("poz")=="ne", r)

    print("\n[7c] TEK DOKUNUŞ düğmeleri (oran tahmini tutmazsa)")
    T("«BANDI TAMAMEN DOLDUR» düğmesi var", pg.locator("#logoBant").count()==1)
    T("«KÖŞEYE BAS» düğmesi var", pg.locator("#logoKose").count()==1)
    r=pg.evaluate("""()=>{B360.S.logoPoz="ne";B360.S.bantYer="yok";B360.S.bantYuk=120;B360.save();
      document.querySelector("#logoBant").click();
      return {poz:B360.S.logoPoz,yer:B360.S.bantYer,yuk:B360.S.bantYuk}}""")
    T("düğme konumu 'bandı kapla' yapıyor", r.get("poz")=="dalt", r)
    T("düğme bant düzenini ve kalınlığını hazırlıyor", r.get("yer")=="alt" and r.get("yuk")==240, r)
    r=pg.evaluate("""()=>{document.querySelector("#logoKose").click();
      return {poz:B360.S.logoPoz}}""")
    T("«köşeye bas» geri alıyor", r.get("poz")=="ne", r)

    print("\n[7d] Eşik 2,5 — 3:1 dosya da şerit sayılıyor (17 Eyl sahada tutmadı)")
    r=pg.evaluate("""()=>{
      const B=B360; B.S.logoPid=""; B.S.logoPoz="ne"; B.S.bantYer="yok"; B.save();
      const c=document.createElement("canvas"); c.width=900; c.height=300;
      const x=c.getContext("2d"); x.fillStyle="#fff"; x.fillRect(0,0,900,300);
      return new Promise(ok=>c.toBlob(b=>{
        const f=new File([b],"serit3.png",{type:"image/png"});
        const dt=new DataTransfer(); dt.items.add(f);
        const inp=document.querySelector("#logoFile");
        inp.files=dt.files; inp.dispatchEvent(new Event("change",{bubbles:true}));
        setTimeout(()=>ok({poz:B.S.logoPoz}),2500);
      },"image/png"));
    }""")
    T("3:1 dosya şerit sayılıyor", r.get("poz")=="dalt", r)
    r=pg.evaluate("""()=>{
      const B=B360; B.S.logoPid=""; B.S.logoPoz="ne"; B.save();
      const c=document.createElement("canvas"); c.width=400; c.height=200;
      const x=c.getContext("2d"); x.fillStyle="#fff"; x.fillRect(0,0,400,200);
      return new Promise(ok=>c.toBlob(b=>{
        const f=new File([b],"genis.png",{type:"image/png"});
        const dt=new DataTransfer(); dt.items.add(f);
        const inp=document.querySelector("#logoFile");
        inp.files=dt.files; inp.dispatchEvent(new Event("change",{bubbles:true}));
        setTimeout(()=>ok({poz:B.S.logoPoz}),2500);
      },"image/png"));
    }""")
    T("2:1 normal logo şerit SAYILMIYOR", r.get("poz")=="ne", r)

    print("\n[8] Sayfa hatası yok")
    T("JS hatası yok", not errs, errs)
    b.close()

print(f"\nSONUÇ: {ok}/{ok+bad} geçti")
sys.exit(0 if bad==0 else 1)
