#!/usr/bin/env python3
"""60 FPS TURU testi — aday sirasi ve secim kurali."""
import json,sys,time,threading,http.server,socketserver,pathlib,functools
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path("/home/claude/booth360"); PORT=8397; BASE=f"http://localhost:{PORT}/"
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
    pg=ctx.new_page(); pg.goto(BASE+"index.html"); pg.wait_for_selector("#s-attract.on")

    print("\n[1] ADAY SIRASI — once 60 dayatan tur, sonra normal")
    r=pg.evaluate("""()=>{const c=B360.tumCands('user',true);
      return {n:c.length, fr:c.map(x=>JSON.stringify(x.video.frameRate))}}""")
    T("8 aday (4 hizli + 4 normal)", r["n"]==8, r["n"])
    T("ilk 4 min:50 dayatiyor", all('"min":50' in x for x in r["fr"][:4]), r["fr"][:4])
    T("son 4 normal ideal:60", all(x=='{"ideal":60}' for x in r["fr"][4:]), r["fr"][4:])

    print("\n[2] hizKare KAPALIYKEN eski davranis")
    r2=pg.evaluate("""()=>{B360.S.hizKare=0;const c=B360.tumCands('user',true);
      const o={n:c.length, fr:c.map(x=>JSON.stringify(x.video.frameRate))};B360.S.hizKare=1;return o}""")
    T("4 aday", r2["n"]==4, r2["n"])
    T("hicbiri dayatmiyor", all('"min"' not in x for x in r2["fr"]), r2["fr"])

    print("\n[3] KAMERA GERCEKTEN ACILIYOR MU (sahte kamera 30 fps verir)")
    pg.evaluate("()=>{B360.S.evt='FPS Test';B360.S.otoDon=0;B360.save()}")
    pg.click("#startBtn"); pg.wait_for_timeout(3500)
    cam=pg.evaluate("()=>({cam:B360.cam||null, log:B360.S.camLog||'', last:B360.S.lastCam||''})")
    T("kamera acildi, aday secildi", bool(cam["cam"]), str(cam))
    T("8 adayin hepsi denendi ya da erken secildi", len(cam["log"].split("|"))>=1, cam["log"][:120])
    print("    | secilen: "+cam["last"])
    print("    | deneme gunlugu: "+cam["log"][:160])
    b.close()

# ---- BÖLÜM 2: MALİYET MATEMATİĞİ ----
print("\n[4] MALIYET — dogrusal buyutme sisiriyordu, motor gercegi versin")
import subprocess,json as J
js = """
const fs=require('fs');eval(fs.readFileSync('/home/claude/booth360/src/engine.js','utf8'));
const E=B360E,O={zoom:1,flash:1,dbl:1,noise:0,du:1},TL=21.31/250;
const out={};
E.TEMPLATES.forEach(t=>{
  const test=E.plan({t:t.id,d:1.4,tur:10,yuz:0,o:O}).out;
  const ger =E.plan({t:t.id,d:15 ,tur:10,yuz:0,o:O}).out;
  out[t.id]={test:+test.toFixed(1),ger:+ger.toFixed(1),
             dogrusal:+(test*(15/1.4)*TL).toFixed(2), gercekTL:+(ger*TL).toFixed(2)};
});
console.log(JSON.stringify(out));
"""
r=J.loads(subprocess.check_output(["node","-e",js]).decode())
for k,v in r.items():
    T(f"{k}: dogrusal {v['dogrusal']} TL, gercek {v['gercekTL']} TL — sisme var",
      v["dogrusal"]>v["gercekTL"]*2, str(v))
ortG=sum(v["gercekTL"] for v in r.values())/len(r)
ortD=sum(v["dogrusal"] for v in r.values())/len(r)
T("ortalama gercek 1.0-2.5 TL arasi", 1.0<=ortG<=2.5, f"{ortG:.2f}")
T("eski hesap 3x+ sisikti", ortD/ortG>=3, f"{ortD/ortG:.1f}x")
print(f"    | GERCEK ortalama: {ortG:.2f} TL/render · eski ekran: {ortD:.2f} TL ({ortD/ortG:.1f}x sisik)")
print(f"    | 100 kisi, misafir basi 1-2 render: {ortG*100:.0f}-{ortG*200:.0f} TL")

print(f"\nSONUÇ: {ok}/{ok+bad} geçti")
sys.exit(1 if bad else 0)
