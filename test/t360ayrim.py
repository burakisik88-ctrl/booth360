#!/usr/bin/env python3
"""OBSKURA 360 — ETKİNLİK AYRIMI testi (8 Eyl 2026).
   Burak'ın sorusu: "iki booth aynı günde farklı etkinlikte olursa ne olacak?"
   Sayım CİHAZ bazlı değil İŞ (etkinlik adı) bazlı. Bu dosya iki şeyi kanıtlar:
     1) İki farklı iş aynı gün hiç karışmıyor (etiket, galeri, rapor, sayaç ayrı)
     2) Aynı iş iki booth'ta birleşiyor
   ve asıl saha riskini kapatan uyarıyı doğrular:
     3) Ad değişmeden ikinci işe girilirse booth ve saha kontrolü UYARIYOR
"""

import json,sys,time,threading,http.server,socketserver,pathlib,functools,datetime
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path("/home/claude/booth360")
PORT=8395; BASE=f"http://localhost:{PORT}/"
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address=True
    with socketserver.TCPServer(("127.0.0.1",PORT),functools.partial(Q,directory=str(ROOT))) as h: h.serve_forever()
threading.Thread(target=serve,daemon=True).start(); time.sleep(0.4)

SAYI={"gala-gecesi-360":12,"acar-dugun-360":3}
def liste(tag):
    n=SAYI.get(tag,0)
    return {"resources":[{"public_id":f"booth360/x/v{i}","created_at":f"2026-09-08T2{i%3}:1{i%6}:00Z"} for i in range(n)]}

ok=0;bad=0
def T(name,cond,extra=""):
    global ok,bad
    if cond: ok+=1; print(f"  ok   {name}")
    else: bad+=1; print(f"  FAIL {name}  -> {extra}")

with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox","--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream","--autoplay-policy=no-user-gesture-required"])
    ctx=b.new_context(viewport={"width":430,"height":932},permissions=["camera"],timezone_id="Europe/Istanbul")
    def route(r):
        u=r.request.url
        for tag in SAYI:
            if f"/video/list/{tag}.json" in u:
                r.fulfill(status=200,content_type="application/json",body=json.dumps(liste(tag))); return
        if "/video/list/" in u: r.fulfill(status=404,body="nf"); return
        r.fulfill(status=200,body="")
    ctx.route("**/*cloudinary.com/**",route)
    pg=ctx.new_page()

    def kur(evt,sayac=None):
        st={"evt":evt,"cldName":"rqhgtbvd","cldPreset":"booth_qr","otoDon":0,"warm":0,
            "sayac":sayac or {}}
        pg.goto(BASE+"index.html"); pg.wait_for_selector("#s-attract.on")
        pg.evaluate("(s)=>{localStorage.setItem('booth360.v1',s)}",json.dumps(st))
        pg.reload(); pg.wait_for_selector("#s-attract.on"); pg.wait_for_timeout(250)

    def sor():
        return pg.evaluate("""()=>new Promise(r=>{B360.bulutSayim(x=>r({
            sayi:x.sayi, metin:B360.sayacMetin(), galeri:B360.galeriUrl(), rapor:B360.raporUrl()}))})""")

    print("\n[1] BOOTH 1 — 'Gala Gecesi' (bulutta 12 video)")
    kur("Gala Gecesi")
    a=sor()
    T("etiket etkinlik adindan turuyor","gala-gecesi-360" in a["galeri"],a["galeri"][-60:])
    T("bulut sayisi 12",a["sayi"]==12,a["sayi"])
    T("obur isi hic gormuyor","acar" not in a["galeri"]+a["rapor"]+a["metin"])

    print("\n[2] BOOTH 2 — AYNI GUN 'Acar Dugun' (bulutta 3 video)")
    kur("Acar Dugun")
    c=sor()
    T("bulut sayisi 3, 12 degil",c["sayi"]==3,c["sayi"])
    T("galeri etiketi ayri","acar-dugun-360" in c["galeri"],c["galeri"][-60:])
    T("rapor etiketi de ayri","acar-dugun-360" in c["rapor"],c["rapor"][-90:])
    T("obur isi hic gormuyor","gala" not in c["galeri"]+c["rapor"]+c["metin"])
    T("iki is toplanmiyor (15 cikmiyor)",c["sayi"]!=15,c["sayi"])

    print("\n[3] TEK CIHAZ, ayni gun iki farkli ise girdi — yerel sayac")
    kur("Gala Gecesi",{"gala-gecesi":{"cekim":9,"teslim":9,"gun":{}},
                       "acar-dugun":{"cekim":3,"teslim":2,"gun":{}}})
    m1=pg.evaluate("()=>B360.sayacMetin()")
    kur("Acar Dugun",{"gala-gecesi":{"cekim":9,"teslim":9,"gun":{}},
                      "acar-dugun":{"cekim":3,"teslim":2,"gun":{}}})
    m2=pg.evaluate("()=>B360.sayacMetin()")
    T("Gala ekraninda 9 cekim",("9 çekim" in m1),m1[:120])
    T("Acar ekraninda 3 cekim",("3 çekim" in m2),m2[:120])
    T("ikisi karismiyor",("9 çekim" not in m2 and "3 çekim" not in m1))

    print("\n[4] AYNI etkinlik iki cihaz — burasi BIRLESMELI")
    kur("Gala Gecesi",{"gala-gecesi":{"cekim":5,"teslim":5,"gun":{}}})
    d=sor()
    T("toplam 12 (bulut), bu telefon 5",d["sayi"]==12 and "5 çekim" in d["metin"],d["metin"][:160])
    T("iki rakam ayri yaziliyor","TÜM BOOTH" in d["metin"] and "Bu telefon" in d["metin"])
    print("\n  ekranda ne yaziyor:")
    for satir in d["metin"].split("\n"): print("    | "+satir)
    b.close()

# ---- BÖLÜM 2: BAYAT AD ----
BUGUN=datetime.datetime.now()
DUN=BUGUN-datetime.timedelta(days=3)
def rs(dt,n):
    return {"resources":[{"public_id":f"booth360/gala-gecesi/v{i}",
            "created_at":dt.strftime("%Y-%m-%dT")+f"2{i%3}:1{i%6}:00Z"} for i in range(n)]}
MOD={"v":"eski"}

with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox","--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream","--autoplay-policy=no-user-gesture-required"])
    ctx=b.new_context(viewport={"width":430,"height":932},permissions=["camera"],timezone_id="Europe/Istanbul")
    def route(r):
        u=r.request.url
        if "/video/list/gala-gecesi-360.json" in u:
            dt=DUN if MOD["v"]=="eski" else BUGUN
            r.fulfill(status=200,content_type="application/json",body=json.dumps(rs(dt,14))); return
        if "/video/list/" in u: r.fulfill(status=404,body="nf"); return
        if "api.cloudinary.com" in u: r.fulfill(status=200,body="{}"); return
        r.fulfill(status=200,body="")
    ctx.route("**/*cloudinary.com/**",route)
    pg=ctx.new_page()
    st=json.dumps({"evt":"Gala Gecesi","cldName":"rqhgtbvd","cldPreset":"booth_qr","otoDon":0,"warm":0,"sayac":{}})
    ctx.add_init_script("try{localStorage.setItem('booth360.v1',"+json.dumps(st)+")}catch(e){}")

    print("\n[A] BOOTH PANELI — ad 3 gun once kullanilmis")
    pg.goto(BASE+"index.html"); pg.wait_for_selector("#s-attract.on")
    r1=pg.evaluate("""()=>new Promise(r=>{B360.bulutSayim(()=>r({u:B360.bayatAd(),m:B360.sayacMetin()}))})""")
    T("uyari uretiliyor", bool(r1["u"]), r1["u"][:80])
    T("14 video ve tarih yaziyor", "14 video" in r1["u"], r1["u"][:110])
    T("ne yapmasi gerektigi yaziyor", "adını değiştir" in r1["u"])
    T("sayac metninde de gorunuyor", r1["m"].startswith("⚠"), r1["m"][:60])
    print("    | "+r1["u"])

    print("\n[B] AYNI GUN (ayni isin devami) — uyari OLMAMALI")
    MOD["v"]="bugun"
    pg.reload(); pg.wait_for_selector("#s-attract.on")
    r2=pg.evaluate("""()=>new Promise(r=>{B360.bulutSayim(()=>r({u:B360.bayatAd(),m:B360.sayacMetin()}))})""")
    T("uyari yok", r2["u"]=="", r2["u"][:80])
    T("normal sayac", "TÜM BOOTH'LAR: 14" in r2["m"], r2["m"][:90])

    print("\n[C] SAHA KONTROLU (t.html) — ad bayatken KIRMIZI olmali")
    MOD["v"]="eski"
    pg.goto(BASE+"t.html"); pg.wait_for_timeout(600)
    try: pg.click("#basla",timeout=2500)
    except Exception:
        for sel in ["text=Kontrolü başlat","button >> nth=0"]:
            try: pg.click(sel,timeout=2000); break
            except Exception: pass
    pg.wait_for_timeout(9000)
    gal=pg.evaluate("""()=>{var it=[...document.querySelectorAll('.it')];
      var e=it.find(x=>{var n=x.querySelector('.nm');return n&&/Etkinlik galerisi/.test(n.textContent||'')});
      return e?{t:(e.querySelector('.ds')||{}).textContent||'', cls:e.className}:null}""")
    T("galeri karti bulundu", bool(gal), str(gal)[:80])
    if gal:
        T("kart KIRMIZI (err)", "err" in gal["cls"], gal["cls"])
        T("bayat ad uyarisi kartta", "adını değiştir" in gal["t"], gal["t"][:150])
        T("14 video yaziyor", "14 video" in gal["t"])
        print("    | "+" ".join(gal["t"].split())[:230])
    b.close()

print("\nSONUÇ: %d/%d geçti"%(ok,ok+bad))
sys.exit(1 if bad else 0)
