(function(){
"use strict";
var VER="v0.7.0";
var E=B360E;
function $(s){return document.querySelector(s)}
var DEF={evt:"",sure:15,kamera:"user",kadraj:"genis916d",lastCam:"",camLog:"",camPick:{},mod:"editli",paket:"efektli",siteUrl:"",cldName:"rqhgtbvd",cldPreset:"booth_qr",muzikler:[],muzikSec:"",
  turSn:10,yuzSn:0,aktif:[],tplMusic:{},logoPid:"",logoPoz:"ne",logoW:"0.22",
  fxMode:"green",fxPath:"booth360/_fx",fxTol:25,fxHave:{},qrMod:"page",warm:1,
  flags:{zoom:1,flash:1,dbl:1,noise:0,du:1},
  kvkk:"Bu alanda çekilen videolar etkinlik boyunca saklanır ve yalnızca karekod ile size verilir.",
  otoDon:75, sayac:{}, wake:1, pin:"1234", krediTl:21.31, sesli:1, deneme:0, logoZorunlu:0, hamKart:1,
  ust:"OBSKURA 360", bas:"Etrafında *dönen* an", renk:"", markaLogo:0, zip:0,
  yonerge:"Kola bak, gülümse — kol yanından geçerken poz ver!"};
var S={};
try{
  var st=JSON.parse(localStorage.getItem("booth360.v1")||"{}");
  S=Object.assign({},DEF,st);
  S.flags=Object.assign({},DEF.flags,st.flags||{});
  S.tplMusic=Object.assign({},st.tplMusic||{});S.fxHave=Object.assign({},st.fxHave||{});
  if(!Array.isArray(S.muzikler))S.muzikler=[];if(!Array.isArray(S.aktif))S.aktif=[];
}catch(e){S=JSON.parse(JSON.stringify(DEF))}
function save(){try{localStorage.setItem("booth360.v1",JSON.stringify(S))}catch(e){}}
/* AYAR TAŞIMA — Safari 7 gün girilmeyen sitenin hafızasını siler.
   #ayar=<base64> ile açılırsa ayarlar geri yüklenir; panelden yer imi bağlantısı üretilir. */
function ayarYukle(){
  try{
    var m=/[#&]ayar=([^&]+)/.exec(location.hash||"");if(!m)return false;
    var j=JSON.parse(decodeURIComponent(escape(atob(m[1].replace(/-/g,"+").replace(/_/g,"/")))));
    if(!j||typeof j!=="object")return false;
    Object.keys(j).forEach(function(k){if(k!=="sayac")S[k]=j[k]});
    S.flags=Object.assign({},DEF.flags,S.flags||{});
    save();
    try{history.replaceState(null,"",location.pathname)}catch(e){}
    return true;
  }catch(e){return false}
}
var AYAR_GELDI=ayarYukle();
function ayarPaket(){
  var o={};Object.keys(S).forEach(function(k){if(k!=="sayac"&&k!=="camLog"&&k!=="lastCam")o[k]=S[k]});
  return o;
}
function ayarKod(){return JSON.stringify(ayarPaket())}
function ayarBag(){
  try{
    var b=btoa(unescape(encodeURIComponent(ayarKod()))).replace(/\+/g,"-").replace(/\//g,"_");
    return pageBase()+"index.html#ayar="+b;
  }catch(e){return ""}
}
function ayarUygula(txt){
  try{
    var j=JSON.parse(txt);if(!j||typeof j!=="object")return "Metin ayar dosyası değil.";
    Object.keys(j).forEach(function(k){if(k!=="sayac")S[k]=j[k]});
    S.flags=Object.assign({},DEF.flags,S.flags||{});
    if(!Array.isArray(S.muzikler))S.muzikler=[];if(!Array.isArray(S.aktif))S.aktif=[];
    save();return "";
  }catch(e){return "Okunamadı: "+((e&&e.message)||"hata")}
}
/* eski kurulumda kadraj bulanık banttı; bant ekranı kesiyordu → düz banta çevir (bir kez) */
if(S.kadraj==="genis916"&&!S.k2){S.kadraj="genis916d";S.k2=1;save()}
var cur="attract";
/* --- EKRAN UYANIK KALSIN: iPhone çekim ortasında ekranı kapatmasın --- */
var wl=null;
function wakeOn(){
  if(!S.wake||!("wakeLock" in navigator)||wl)return;
  try{navigator.wakeLock.request("screen").then(function(x){wl=x;x.addEventListener&&x.addEventListener("release",function(){wl=null})},function(){})}catch(e){}
}
function wakeOff(){try{if(wl&&wl.release)wl.release()}catch(e){}wl=null}
document.addEventListener("visibilitychange",function(){if(document.visibilityState==="visible"&&cur!=="attract")wakeOn()});
/* --- kayıt/yükleme sırasında sayfadan çıkışa uyarı --- */
var mesgul=false;
window.addEventListener("beforeunload",function(e){if(mesgul){e.preventDefault();e.returnValue=""}});
function go(n){
  document.querySelectorAll(".screen").forEach(function(s){s.classList.remove("on")});
  var el=$("#s-"+n);if(el)el.classList.add("on");
  cur=n;
  $("#gearBtn").style.display=(n==="attract")?"block":"none";
  if(n==="attract"){wakeOff();temizle()}else wakeOn();
  otoDonKur(n);
  var ft=document.querySelector("footer.tag");if(ft)ft.style.display=(n==="admin"||n==="cal")?"none":"block";
}
document.querySelectorAll("[data-go]").forEach(function(b){b.addEventListener("click",function(){go(b.getAttribute("data-go"))})});
/* misafir ekranı bıraktığında bir sonraki misafir önceki videoyu GÖRMESİN */
function temizle(){
  curVid=null;selTpl=null;lastUrl="";lastPage="";muzikAcik=false;
  try{var pv=$("#prevVid");pv.removeAttribute("src");pv.load()}catch(e){}
  try{var c=$("#qrCanvas"),x=c.getContext("2d");x.clearRect(0,0,c.width,c.height)}catch(e){}
  var a=$("#qrAdres");if(a)a.textContent="";
}
var otoT=null;
function otoDonKur(n){
  clearTimeout(otoT);
  var sn=+S.otoDon||0;
  if(!sn)return;
  if(n==="done"||n==="style"||n==="prev"){otoT=setTimeout(function(){if(cur===n)go("attract")},sn*1000)}
}
/* --- ÇEKİM SAYACI (etkinlik bazlı) --- */
function bugun(){var d=new Date();return d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2)}
function sayacArt(tip){
  var k=evSlug();S.sayac=S.sayac||{};
  var o=S.sayac[k]||{cekim:0,teslim:0,gun:{}};
  o[tip]=(o[tip]||0)+1;
  o.gun=o.gun||{};o.gun[bugun()]=(o.gun[bugun()]||0)+1;
  o.son=new Date().toISOString().slice(0,16).replace("T"," ");
  S.sayac[k]=o;save();
}
/* ---- BULUT MALİYETİ (Cloudinary kredisi → TL) ----
   Doğrulanmış oran (07.09.2026): HD video = 250 çıktı saniyesi / kredi.
   Plus plan $99 / 225 kredi = $0,44 kredi → 48,44 TL kur ile 21,31 TL/kredi.
   AYNI adres ikinci kez istendiğinde Cloudinary tekrar ücret almaz — bu yüzden
   yalnız DAHA ÖNCE GÖRÜLMEMİŞ adresler sayılır. */
var gorulenUrl={};
function tlKredi(){return +S.krediTl||21.31}
function snTl(sn){return tlKredi()*(sn/250)}
function maliyetEkle(u,sn){
  if(!u||!(+sn>0)||gorulenUrl[u]||S.deneme)return;
  gorulenUrl[u]=1;
  var k=evSlug();S.sayac=S.sayac||{};
  var o=S.sayac[k]||{cekim:0,teslim:0,gun:{}};
  o.render=(o.render||0)+1;o.sn=Math.round(((o.sn||0)+(+sn||0))*10)/10;
  S.sayac[k]=o;save();
}
function maliyetMetin(){
  var o=(S.sayac||{})[evSlug()]||{},sn=+o.sn||0,r=+o.render||0;
  if(!r)return "Bulut işlemi yok — bu etkinlikte henüz kredi harcanmadı.";
  var kr=sn/250, tl=snTl(sn);
  return r+" bulut render · "+Math.round(sn)+" sn · "+kr.toFixed(2)+" kredi · ≈"+tl.toFixed(0)+" TL"+
         (o.teslim?("  ·  teslim başına ≈"+(tl/o.teslim).toFixed(1)+" TL"):"");
}
/* ÇOK BOOTH: sayaç her telefonun kendi hafızasında tutuluyor — iki booth çalışınca
   sayılar bölünüyor. Gerçek toplam bulutta: aynı etiketle yüklenen videoların sayısı.
   Hangi telefondan geldiği fark etmez. */
var bulut={sayi:null,ilk:"",son:"",saat:null,hata:"",zaman:0};
function bulutSayim(cb){
  var t=evSlug()+"-360";
  var u="https://res.cloudinary.com/"+encodeURIComponent(S.cldName)+"/video/list/"+encodeURIComponent(t)+".json";
  fetch(u,{cache:"no-store"}).then(function(r){
    if(r.status===404){bulut={sayi:0,ilk:"",son:"",saat:{},hata:"",zaman:Date.now()};if(cb)cb(bulut);return}
    if(!r.ok)throw new Error("HTTP "+r.status);
    return r.json().then(function(j){
      var rs=(j.resources||[]).filter(function(x){return String(x.public_id||"").indexOf("/_")<0});
      var saat={},zs=[];
      rs.forEach(function(x){
        var c=x.created_at||"";if(!c)return;
        zs.push(c);
        var h=c.slice(11,13);if(h)saat[h]=(saat[h]||0)+1;
      });
      zs.sort();
      bulut={sayi:rs.length,ilk:zs[0]||"",son:zs[zs.length-1]||"",saat:saat,hata:"",zaman:Date.now()};
      if(cb)cb(bulut);
    });
  }).catch(function(e){
    bulut={sayi:null,ilk:"",son:"",saat:null,hata:(e&&e.message)||"okunamadı",zaman:Date.now()};
    if(cb)cb(bulut);
  });
}
function sayacMetin(){
  var k=evSlug(),o=(S.sayac||{})[k]||{};
  var b=(bulut.sayi!==null)?bulut.sayi:null;
  var t=[];
  if(b!==null)t.push("TÜM BOOTH'LAR: "+b+" video (buluttan sayıldı)");
  else if(bulut.hata)t.push("Bulut sayımı okunamadı ("+bulut.hata+") — aşağıdaki yalnız BU telefonun rakamı");
  t.push("Bu telefon: "+(o.cekim||0)+" çekim, "+(o.teslim||0)+" teslim · bugün "+((o.gun||{})[bugun()]||0));
  if(o.son)t.push("son: "+o.son);
  if(!o.cekim&&b===null)return "Bu etkinlikte henüz çekim yok.";
  return "«"+(S.evt||"etkinlik")+"»  ·  "+t.join("  ·  ");
}
function evSlug(){
  var s=(S.evt||"etkinlik").toString().toLowerCase();
  try{s=s.normalize("NFD").replace(/[̀-ͯ]/g,"")}catch(e){}
  s=s.replace(/ı/g,"i").replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");
  return (s||"etkinlik").slice(0,40);
}
function stem(name){
  var s=String(name||"").replace(/\.[^.]+$/,"").toLowerCase();
  try{s=s.normalize("NFD").replace(/[̀-ͯ]/g,"")}catch(e){}
  return s.replace(/ı/g,"i").replace(/[^a-z0-9_]+/g,"_").replace(/^_+|_+$/g,"").slice(0,40)||"fx";
}
/* PAKET: satış kararının tek yeri.
   editsiz  → şablon yok, ham video (bulutta hiçbir işlem, sıfır kredi)
   sablon   → şablonlu edit (hız/renk/müzik/logo), FX katmanı KAPALI
   efektli  → şablon + FX katmanı (yıldız/kalp/konfeti/sparkle) */
function paketOf(){
  var p=S.paket;
  if(p!=="editsiz"&&p!=="sablon"&&p!=="efektli"){ /* eski sürümden göç */
    p=(S.mod==="editsiz")?"editsiz":((S.fxMode==="off")?"sablon":"efektli");
    S.paket=p;save();
  }
  return p;
}
function paketAd(p){return p==="editsiz"?"Editsiz (ham video)":(p==="sablon"?"Editli · efektsiz":"Editli · efektli")}
function yildizli(t){ /* *kelime* → vurgu rengiyle */
  return String(t||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/\*([^*]+)\*/g,"<em>$1</em>");
}
function applyBrand(){
  var p=paketOf();
  try{
    var u=$("#attractUst");if(u)u.textContent=S.ust||"OBSKURA 360";
    var b=$("#attractBas");if(b)b.innerHTML=yildizli(S.bas||"Etrafında *dönen* an");
    if(/^#[0-9a-fA-F]{3,8}$/.test(S.renk||""))document.documentElement.style.setProperty("--amber",S.renk);
    else document.documentElement.style.removeProperty("--amber");
    var im=$("#markaLogo");
    if(im){
      if(S.markaLogo&&S.logoPid){im.src="https://res.cloudinary.com/"+encodeURIComponent(S.cldName)+"/image/upload/h_220,c_limit/"+S.logoPid;im.hidden=false}
      else{im.hidden=true;im.removeAttribute("src")}
    }
  }catch(e){}
  $("#attractEvt").textContent=(S.evt?S.evt:"15 saniyelik 360° video — çek, telefonuna al.")+(p!=="efektli"?(" · "+paketAd(p)):"")+(S.deneme?"  ·  DENEME MODU":"");
  var kn=$("#kvkkNot");if(kn)kn.textContent=S.kvkk||"";
}
applyBrand();
var SITE_VARSAYILAN="https://burakisik88-ctrl.github.io/booth360/";
function pageBase(){
  /* karekoda YALNIZ http(s) adres yazılır; başka şemadan açılırsa panel adresine düşer
     (iOS kamerası http olmayan adrese "kullanılabilir veri yok" der) */
  if(S.siteUrl&&/^https?:\/\//i.test(S.siteUrl))return S.siteUrl.replace(/[^\/]*$/,"");
  var h=location.href.split(/[?#]/)[0];
  if(/^https?:\/\//i.test(h))return h.replace(/[^\/]*$/,"");
  return SITE_VARSAYILAN;
}
var KADRAJ={genis916:"g916",genis916d:"g916d",genis916k:"g916k"};
function kKodu(){return KADRAJ[S.kadraj]||""}
function logoVar(){return !!(S.logoZorunlu&&S.logoPid)}
function activeTpls(){
  var a=E.TEMPLATES.filter(function(t){return S.aktif.indexOf(t.id)>=0});
  return a.length?a:E.TEMPLATES.slice();
}
function musicFor(tid){return (S.tplMusic&&S.tplMusic[tid])||S.muzikSec||""}

/* ---------- PIN ---------- */
var pinBuf="";
function PINK(){return (S.pin&&/^\d{4}$/.test(S.pin))?S.pin:"1234"}
$("#gearBtn").onclick=function(){pinBuf="";drawPin();go("pin")};
function drawPin(){
  var p=$("#pinPad");
  if(!p.childElementCount){
    ["1","2","3","4","5","6","7","8","9","","0","←"].forEach(function(k){
      var b=document.createElement("button");b.textContent=k;
      if(!k)b.style.visibility="hidden";
      b.onclick=function(){
        if(k==="←")pinBuf=pinBuf.slice(0,-1);else if(k)pinBuf+=k;
        if(pinBuf.length>4)pinBuf=pinBuf.slice(0,4);
        drawPin();
        if(pinBuf.length===4){
          if(pinBuf===PINK()){pinBuf="";drawPin();fillAdmin();go("admin")}
          else{pinBuf="";drawPin()}
        }
      };
      p.appendChild(b);
    });
  }
  var d=$("#pinDots").children;
  for(var i=0;i<4;i++)d[i].className=i<pinBuf.length?"f":"";
}

/* ---------- BULUT YÜKLEME (ortak) ---------- */
function cldUpload(file,kind,fields,onProg){
  return new Promise(function(res,rej){
    var fd=new FormData();
    fd.append("file",file);fd.append("upload_preset",S.cldPreset);
    Object.keys(fields||{}).forEach(function(k){fd.append(k,fields[k])});
    var xhr=new XMLHttpRequest();
    xhr.open("POST","https://api.cloudinary.com/v1_1/"+encodeURIComponent(S.cldName)+"/"+kind+"/upload");
    if(onProg)xhr.upload.onprogress=function(e){if(e.total)onProg(e.loaded/e.total)};
    xhr.onload=function(){
      var j=null;try{j=JSON.parse(xhr.responseText)}catch(e){}
      if(xhr.status>=200&&xhr.status<300&&j&&j.public_id)res(j);
      else rej(new Error((j&&j.error&&j.error.message)||("yükleme reddedildi ("+xhr.status+")")));
    };
    xhr.onerror=function(){rej(new Error("bağlantı hatası"))};
    xhr.send(fd);
  });
}

/* ---------- ADMIN ---------- */
function fillAdmin(){
  $("#fEvt").value=S.evt;$("#fKam").value=S.kamera||"user";$("#fKadraj").value=S.kadraj||"genis916";$("#fPaket").value=paketOf();
  paketNot();
  $("#fOto").value=S.otoDon;$("#fWake").value=S.wake?"1":"0";$("#fKvkk").value=S.kvkk||"";
  $("#fSesli").value=S.sesli?"1":"0";$("#fPin").value=PINK();$("#fYonerge").value=S.yonerge||"";
  $("#fUst").value=S.ust||"";$("#fBas").value=S.bas||"";$("#fRenk").value=S.renk||"";
  $("#fMarkaLogo").value=S.markaLogo?"1":"0";$("#fkZip").checked=!!S.zip;markaNot();
  $("#fkDeneme").checked=!!S.deneme;denemeNot();
  $("#fKredi").value=tlKredi();
  $("#maliyetNot").textContent=maliyetMetin();
  durumYaz();
  $("#sayacNot").textContent=sayacMetin();
  bulutSayim(function(){$("#sayacNot").textContent=sayacMetin()});
  $("#galeriNot").textContent="Galeri: "+galeriUrl();
  $("#camInfo").textContent=(S.lastCam?("Son çekim: "+S.lastCam):"Henüz çekim yok.")+(S.camLog?("  ·  Denenen: "+S.camLog):"");
  var fs=$("#fSure");if(!Array.prototype.some.call(fs.options,function(o){return o.value===String(S.sure)})){var op=document.createElement("option");op.value=String(S.sure);op.textContent=S.sure+" saniye";fs.appendChild(op)}
  fs.value=String(S.sure);
  $("#fCld").value=S.cldName;$("#fPreset").value=S.cldPreset;$("#fQr").value=S.qrMod;$("#fSite").value=S.siteUrl||"";
  $("#fTur").value=S.turSn;$("#fYuz").value=S.yuzSn;
  $("#fLogoPoz").value=S.logoPoz;$("#fLogoW").value=String(S.logoW);
  $("#fFx").value=S.fxMode;$("#fTol").value=S.fxTol;
  $("#fLogoZor").value=S.logoZorunlu?"1":"0";$("#fHamKart").value=(S.hamKart===0)?"0":"1";logoZorNot();
  $("#fkWarm").checked=!!S.warm;$("#fkDbl").checked=!!S.flags.dbl;$("#fkZoom").checked=!!S.flags.zoom;
  $("#fkFlash").checked=!!S.flags.flash;$("#fkNoise").checked=!!S.flags.noise;$("#fkDu").checked=!!S.flags.du;
  buildTplList();buildMuzikList();logoInfo();fxInfo();
  fxProbe(function(ch){if(ch)fxInfo()});
  $("#verNote").textContent="OBSKURA 360 · "+VER+" · PIN 1234 · Videolar: booth360/"+evSlug()+" · İzleme sayfası: "+pageBase()+"v.html";
  try{$("#taniTxt").value=JSON.stringify({ver:VER,evt:S.evt,paket:paketOf(),mod:S.mod,kamera:S.kamera,kadraj:S.kadraj,sure:S.sure,muzikler:S.muzikler,muzikSec:S.muzikSec,tplMusic:S.tplMusic,fxHave:S.fxHave,fxMode:S.fxMode,logo:S.logoPid,aktif:S.aktif,tur:S.turSn,yuz:S.yuzSn,flags:S.flags,lastCam:S.lastCam,camLog:S.camLog,lastUrl:lastUrl,lastPage:lastPage,ua:navigator.userAgent})}catch(e){}
}
$("#fEvt").addEventListener("input",function(){S.evt=this.value;save();applyBrand()});
$("#fSure").addEventListener("change",function(){S.sure=Math.max(5,Math.min(30,+this.value||15));save()});
$("#fKam").addEventListener("change",function(){S.kamera=this.value;save()});
$("#fKadraj").addEventListener("change",function(){S.kadraj=this.value;save()});
function paketNot(){
  var p=paketOf(),t="";
  if(p==="editsiz")t="Misafir çekilen videoyu olduğu gibi alır. Şablon ekranı çıkmaz, karekod hemen gelir. Bulutta işlem yok — yalnız depolama/indirme.";
  else if(p==="sablon")t="Şablonlar çalışır (hız eğrisi, renk, müzik, logo) ama efekt katmanı eklenmez. Efekt videoları yüklü olsa bile kullanılmaz.";
  else t="Şablon + efekt katmanı (yıldız, kalp, konfeti, sparkle). En yüksek bulut maliyeti — efektli iş sattığında aç.";
  $("#paketNot").textContent=t;
  $("#fxGrp").style.opacity=(p==="efektli")?"1":".45";
  $("#fxKapali").textContent=(p==="efektli")?"":"Bu pakette efekt katmanı kapalı — ayarlar saklanır, kullanılmaz.";
}
$("#fPaket").addEventListener("change",function(){
  S.paket=this.value;S.mod=(this.value==="editsiz")?"editsiz":"editli"; /* eski alan uyumlu kalsın */
  save();applyBrand();paketNot();
});
$("#taniKopyala").onclick=function(){var t=$("#taniTxt");t.select();try{navigator.clipboard.writeText(t.value).then(function(){$("#taniNot").textContent="Kopyalandı — sohbete yapıştır."})}catch(e){document.execCommand("copy");$("#taniNot").textContent="Kopyalandı — sohbete yapıştır."}};
$("#fCld").addEventListener("input",function(){S.cldName=this.value.trim();save()});
$("#fPreset").addEventListener("input",function(){S.cldPreset=this.value.trim();save()});
$("#fQr").addEventListener("change",function(){S.qrMod=this.value;save()});
$("#fSite").addEventListener("input",function(){S.siteUrl=this.value.trim();save()});
$("#fOto").addEventListener("change",function(){S.otoDon=Math.max(0,Math.min(600,+this.value||0));this.value=S.otoDon;save()});
$("#fWake").addEventListener("change",function(){S.wake=this.value==="1"?1:0;save()});
$("#fKvkk").addEventListener("input",function(){S.kvkk=this.value;save();applyBrand()});
function raporUrl(){return pageBase()+"r.html#c="+encodeURIComponent(S.cldName)+"&t="+encodeURIComponent(evSlug()+"-360")+"&e="+encodeURIComponent(S.evt||"Etkinlik")+"&g="+encodeURIComponent(galeriUrl())}
function galeriUrl(){return pageBase()+"g.html#c="+encodeURIComponent(S.cldName)+"&t="+encodeURIComponent(evSlug()+"-360")+"&e="+encodeURIComponent(S.evt||"Etkinlik")+(S.zip?"&z=1":"")}
$("#galeriAc").onclick=function(){window.open(galeriUrl(),"_blank")};
$("#galeriKopya").onclick=function(){var b=$("#galeriKopya");try{navigator.clipboard.writeText(galeriUrl()).then(function(){b.textContent="Kopyalandı"})}catch(e){}
  setTimeout(function(){b.textContent="Galeri bağlantısını kopyala"},2500)};
$("#sayacSifirla").onclick=function(){if(S.sayac)delete S.sayac[evSlug()];save();$("#sayacNot").textContent=sayacMetin();$("#maliyetNot").textContent=maliyetMetin()};
$("#raporAc").onclick=function(){window.open(raporUrl(),"_blank")};
$("#raporKopya").onclick=function(){var b=$("#raporKopya");try{navigator.clipboard.writeText(raporUrl()).then(function(){b.textContent="Kopyalandı"})}catch(e){}
  setTimeout(function(){b.textContent="Rapor bağlantısını kopyala"},2500)};
$("#sayacYenile").onclick=function(){$("#sayacNot").textContent="Buluttan sayılıyor…";bulutSayim(function(){$("#sayacNot").textContent=sayacMetin()})};
$("#fSesli").addEventListener("change",function(){S.sesli=this.value==="1"?1:0;save();if(S.sesli)bip(880,120)});
$("#fPin").addEventListener("input",function(){var v=this.value.replace(/\D/g,"").slice(0,4);this.value=v;if(v.length===4){S.pin=v;save()}});
$("#fYonerge").addEventListener("input",function(){S.yonerge=this.value;save()});
function markaNot(){
  var n=$("#markaLogo Not")||$("#markaNot");if(!n)return;
  var t=[];
  if(S.markaLogo&&!S.logoPid)t.push("Logo yüklü değil — önce Logo bölümünden yükle.");
  if(S.renk&&!/^#[0-9a-fA-F]{3,8}$/.test(S.renk))t.push("Renk kodu geçersiz, # ile başlamalı (örn. #C8102E).");
  n.className="note"+(t.length?" err":"");
  n.textContent=t.length?t.join(" "):"Misafirin gördüğü ilk ekran. Kurumsal işte müşterinin logosunu ve rengini koy — videoya basılan logodan ayrı bir şey.";
}
$("#fUst").addEventListener("input",function(){S.ust=this.value;save();applyBrand()});
$("#fBas").addEventListener("input",function(){S.bas=this.value;save();applyBrand()});
$("#fRenk").addEventListener("input",function(){S.renk=this.value.trim();save();applyBrand();markaNot()});
$("#fMarkaLogo").addEventListener("change",function(){S.markaLogo=this.value==="1"?1:0;save();applyBrand();markaNot()});
$("#fkZip").addEventListener("change",function(){S.zip=this.checked?1:0;save();$("#galeriNot").textContent="Galeri: "+galeriUrl()});
function denemeNot(){$("#denemeNot").textContent=S.deneme
  ?"AÇIK — çekimler booth360/_deneme klasörüne gider, sayaç ve maliyet artmaz, misafir galerisine düşmez. Etkinlik başlarken KAPAT."
  :"Kapalı — çekimler etkinlik klasörüne ve galerisine gidiyor."}
$("#fkDeneme").addEventListener("change",function(){S.deneme=this.checked?1:0;save();denemeNot();applyBrand()});
$("#fKredi").addEventListener("change",function(){S.krediTl=Math.max(1,Math.min(500,+this.value||21.31));this.value=S.krediTl;save();$("#maliyetNot").textContent=maliyetMetin()});
$("#maliyetSifirla").onclick=function(){var k=evSlug();if(S.sayac&&S.sayac[k]){S.sayac[k].render=0;S.sayac[k].sn=0;save()}gorulenUrl={};$("#maliyetNot").textContent=maliyetMetin()};
/* --- SAHA DURUMU: batarya + internet (telefon %5'te kalmasın, wifi gittiğini gör) --- */
function durumYaz(){
  var net=navigator.onLine?"İnternet: VAR":"İNTERNET YOK";
  var el=$("#durumNot");if(!el)return;
  el.className="note"+(navigator.onLine?" ok":" err");
  el.textContent=net;
  try{
    if(navigator.getBattery)navigator.getBattery().then(function(b){
      var y=Math.round(b.level*100);
      el.className="note"+((navigator.onLine&&y>20)?" ok":" err");
      el.textContent=net+"  ·  Batarya: %"+y+(b.charging?" (şarjda)":"")+(y<=20&&!b.charging?"  ← ŞARJA TAK":"");
    });
  }catch(e){}
}
window.addEventListener("online",durumYaz);window.addEventListener("offline",durumYaz);
/* --- AYAR YEDEĞİ --- */
function yedekNot(t,err){var n=$("#yedekNot");n.className="note"+(err?" err":" ok");n.textContent=t;setTimeout(function(){if(n.textContent===t){n.className="note";n.textContent=""}},6000)}
function kopyala(t,ok){try{navigator.clipboard.writeText(t).then(function(){yedekNot(ok)},function(){yedekNot("Kopyalanamadı — 'Göster / yapıştır' ile elle al.",1)})}catch(e){yedekNot("Kopyalanamadı — 'Göster / yapıştır' ile elle al.",1)}}
$("#testAc").onclick=function(){window.open(pageBase()+"t.html","_blank")};
$("#yedekBag").onclick=function(){var b=ayarBag();if(!b){yedekNot("Bağlantı üretilemedi.",1);return}$("#yedekTxt").hidden=false;$("#yedekTxt").value=b;kopyala(b,"Bağlantı kopyalandı — Notlar'a yapıştır ve yer imine ekle. Hafıza silinirse bu bağlantıyı aç, ayarlar geri gelir.")};
$("#yedekKopya").onclick=function(){var t=ayarKod();$("#yedekTxt").hidden=false;$("#yedekTxt").value=t;kopyala(t,"Ayar metni kopyalandı — Notlar'a yapıştırıp sakla.")};
$("#yedekGoster").onclick=function(){var t=$("#yedekTxt");t.hidden=!t.hidden;$("#yedekYukleRow").hidden=t.hidden;if(!t.hidden&&!t.value)t.value=ayarKod()};
$("#yedekYukle").onclick=function(){
  var e=ayarUygula($("#yedekTxt").value);
  if(e){yedekNot(e,1);return}
  yedekNot("Ayarlar yüklendi.");fillAdmin();applyBrand();
};
$("#fTur").addEventListener("change",function(){S.turSn=Math.max(2,Math.min(60,+this.value||10));this.value=S.turSn;save()});
$("#fYuz").addEventListener("change",function(){S.yuzSn=Math.max(0,Math.min(60,+this.value||0));this.value=S.yuzSn;save()});
$("#fLogoPoz").addEventListener("change",function(){S.logoPoz=this.value;save()});
function logoZorNot(){
  var n=$("#logoZorNot");if(!n)return;
  if(!S.logoPid){n.className="note err";n.textContent="Logo yüklü değil — zorunlu seçsen de basılamaz.";return}
  n.className="note";
  n.textContent=S.logoZorunlu
    ? "Şablonsuz videoya da logo basılır. Bu, o videoyu bulut işleminden geçirir: ≈"+snTl(S.sure).toFixed(2)+" TL/misafir. Müşteri \u201cherkesin videosunda logo olsun\u201d diyorsa bunu seç."
    : "Şablonsuz seçen misafir videoyu logosuz ve bulut maliyeti olmadan alır (0 TL, anında).";
}
$("#fLogoZor").addEventListener("change",function(){S.logoZorunlu=this.value==="1"?1:0;save();logoZorNot()});
$("#fHamKart").addEventListener("change",function(){S.hamKart=this.value==="1"?1:0;save()});
$("#fLogoW").addEventListener("change",function(){S.logoW=this.value;save()});
$("#fFx").addEventListener("change",function(){S.fxMode=this.value;save()});
$("#fTol").addEventListener("change",function(){S.fxTol=Math.max(0,Math.min(100,+this.value||25));this.value=S.fxTol;save()});
[["fkWarm","warm"],["fkDbl","dbl"],["fkZoom","zoom"],["fkFlash","flash"],["fkNoise","noise"],["fkDu","du"]].forEach(function(p){
  $("#"+p[0]).addEventListener("change",function(){
    if(p[1]==="warm")S.warm=this.checked?1:0;else S.flags[p[1]]=this.checked?1:0;save();
  });
});
function buildTplList(){
  var w=$("#tplList");w.innerHTML="";
  E.TEMPLATES.forEach(function(t){
    var r=document.createElement("div");r.className="mrow";
    var ck=document.createElement("input");ck.type="checkbox";ck.style.cssText="width:22px;height:22px;accent-color:var(--amber)";
    ck.checked=S.aktif.length?S.aktif.indexOf(t.id)>=0:true;
    ck.onchange=function(){
      var a=activeTpls().map(function(x){return x.id});
      if(ck.checked){if(a.indexOf(t.id)<0)a.push(t.id)}else a=a.filter(function(x){return x!==t.id});
      S.aktif=E.TEMPLATES.map(function(x){return x.id}).filter(function(id){return a.indexOf(id)>=0});
      if(!S.aktif.length){S.aktif=[t.id];ck.checked=true}
      save();buildTplList();
    };
    var nm=document.createElement("div");nm.className="nm";nm.textContent=t.e+" "+t.n+(t.fx?" · FX: "+t.fx:"");
    var sel=document.createElement("select");
    var o0=document.createElement("option");o0.value="";o0.textContent="🎵 genel";sel.appendChild(o0);
    S.muzikler.forEach(function(m){var o=document.createElement("option");o.value=m.pid;o.textContent=m.n;sel.appendChild(o)});
    sel.value=(S.tplMusic[t.id]&&S.muzikler.some(function(m){return m.pid===S.tplMusic[t.id]}))?S.tplMusic[t.id]:"";
    sel.onchange=function(){if(sel.value)S.tplMusic[t.id]=sel.value;else delete S.tplMusic[t.id];save()};
    r.appendChild(ck);r.appendChild(nm);r.appendChild(sel);w.appendChild(r);
  });
}
/* müzik */
$("#muzikBtn").onclick=function(){$("#muzikFile").click()};
$("#muzikFile").addEventListener("change",function(){
  var f=this.files&&this.files[0];this.value="";if(!f)return;
  var w=$("#muzikList");
  var st=document.createElement("div");st.className="note";st.textContent="Müzik yükleniyor…";w.appendChild(st);
  cldUpload(f,"video",{folder:"booth360/_muzik"}).then(function(j){
    S.muzikler.push({n:f.name.replace(/\.[^.]+$/,""),pid:j.public_id});
    if(!S.muzikSec)S.muzikSec=j.public_id;
    save();buildMuzikList();buildTplList();
  }).catch(function(e){st.textContent="Müzik yüklenemedi: "+((e&&e.message)||"hata");st.className="note err";setTimeout(function(){if(st.parentNode)st.parentNode.removeChild(st)},6000)});
});
function buildMuzikList(){
  var w=$("#muzikList");w.innerHTML="";
  if(!S.muzikler.length){var d=document.createElement("div");d.className="note";d.textContent="Henüz müzik yok.";w.appendChild(d);return}
  S.muzikler.forEach(function(m){
    var r=document.createElement("div");r.className="mrow";
    var nm=document.createElement("div");nm.className="nm";nm.textContent=(S.muzikSec===m.pid?"🎵 ":"")+m.n;
    var sec=document.createElement("button");sec.className="btn ghost mini";sec.textContent=S.muzikSec===m.pid?"Genel (seçili)":"Genel yap";
    sec.onclick=function(){S.muzikSec=m.pid;save();buildMuzikList()};
    var sil=document.createElement("button");sil.className="btn ghost mini";sil.textContent="Sil";
    sil.onclick=function(){S.muzikler=S.muzikler.filter(function(x){return x.pid!==m.pid});if(S.muzikSec===m.pid)S.muzikSec=S.muzikler.length?S.muzikler[0].pid:"";
      Object.keys(S.tplMusic).forEach(function(k){if(S.tplMusic[k]===m.pid)delete S.tplMusic[k]});save();buildMuzikList();buildTplList()};
    var tst=document.createElement("button");tst.className="btn ghost mini";tst.textContent="▶ Test";
    tst.onclick=function(){ /* 1) parça buluttan çalıyor mu 2) sesli test klibi (sparkle FX + bu müzik) hazırlanıyor mu */
      var st=document.createElement("div");st.className="note";st.textContent="Parça çalınıyor… (ses açık mı?)";r.appendChild(st);
      var a=new Audio("https://res.cloudinary.com/"+encodeURIComponent(S.cldName)+"/video/upload/"+m.pid+".mp3");a.play().catch(function(e){st.textContent="Parça çalınamadı: "+(e&&e.message||"hata")});
      var tu="https://res.cloudinary.com/"+encodeURIComponent(S.cldName)+"/video/upload/so_0,du_3/l_audio:"+m.pid.replace(/\//g,":")+",du_3.5/fl_layer_apply/"+S.fxPath+"/sparkle.mp4";
      fetch(tu,{method:"HEAD",cache:"no-store"}).then(function(x){st.textContent+=" · Bulut ses katmanı testi: HTTP "+x.status+(x.status===200?" (tamam)":" (HATA)")}).catch(function(){st.textContent+=" · Bulut testi: bağlantı yok"});
      setTimeout(function(){try{a.pause()}catch(e){}},6000);
    };
    r.appendChild(nm);r.appendChild(sec);r.appendChild(tst);r.appendChild(sil);w.appendChild(r);
  });
}
/* logo */
function logoInfo(){var n=$("#logoInfo");n.className="note"+(S.logoPid?" ok":"");n.textContent=S.logoPid?("Logo yüklü: "+S.logoPid):"Logo yok — videoya logo binmez."}
$("#logoBtn").onclick=function(){$("#logoFile").click()};
$("#logoFile").addEventListener("change",function(){
  var f=this.files&&this.files[0];this.value="";if(!f)return;
  var n=$("#logoInfo");n.className="note";n.textContent="Logo yükleniyor…";
  cldUpload(f,"image",{folder:"booth360/_logo"}).then(function(j){S.logoPid=j.public_id;save();logoInfo();logoZorNot()})
    .catch(function(e){n.className="note err";n.textContent="Logo yüklenemedi: "+((e&&e.message)||"hata")});
});
$("#logoDel").onclick=function(){S.logoPid="";save();logoInfo();logoZorNot()};
/* FX */
function fxInfo(){
  var n=$("#fxInfo"),h=Object.keys(S.fxHave||{});
  n.className="note"+(h.length?" ok":"");
  n.textContent=h.length?("Yüklü FX: "+h.join(", ")):"Henüz FX videosu yüklenmedi — şablonlar FX'siz çalışır (FX'i Kapalı yap ya da videoları yükle).";
}
$("#fxBtn").onclick=function(){$("#fxFile").click()};
$("#fxFile").addEventListener("change",function(){
  var files=Array.prototype.slice.call(this.files||[]);this.value="";if(!files.length)return;
  var n=$("#fxInfo");n.className="note";var done=0,fail=[];
  n.textContent="FX yükleniyor… 0/"+files.length;
  function next(){
    if(!files.length){fxInfo();if(fail.length){n.className="note err";n.textContent+=" — HATA: "+fail.join("; ")}return}
    var f=files.shift(),id=stem(f.name);
    cldUpload(f,"video",{public_id:S.fxPath+"/"+id},function(p){n.textContent="FX yükleniyor… "+done+"/"+(done+files.length+1)+" ("+id+" %"+Math.round(p*100)+")"})
      .then(function(j){S.fxHave[id]=j.public_id;save();done++;next()})
      .catch(function(e){fail.push(id+": "+((e&&e.message)||"hata"));next()});
  }
  next();
});

/* ---------- KAYIT ---------- */
var stream=null,rec=null,chunks=[],recTimer=null,recWatch=null,lastBlobUrl="";
var recBusy=false;
$("#startBtn").onclick=function(){if(recBusy)return;recBusy=true;$("#startBtn").disabled=true;setTimeout(function(){$("#startBtn").disabled=false},1200);beginRec()};
function camCands(fm,wide){
  var fr={ideal:60};
  if(!wide)return [{video:{facingMode:fm,width:{ideal:1080},height:{ideal:1920},frameRate:fr},audio:false}];
  /* geniş kadraj: sensörün 4:3 modu. iOS bazı isteklerde kareyi yatay verir; adaylar sırayla denenir, DİKEY ve en geniş olan seçilir */
  return [
    {video:{facingMode:fm,width:{ideal:1440},height:{ideal:1920},frameRate:fr},audio:false},
    {video:{facingMode:fm,width:{ideal:1920},height:{ideal:1440},frameRate:fr},audio:false},
    {video:{facingMode:fm,aspectRatio:{ideal:0.75},height:{ideal:1920},frameRate:fr},audio:false},
    {video:{facingMode:fm,width:{ideal:1080},height:{ideal:1920},frameRate:fr},audio:false}
  ];
}
/* akışı aç, gerçek kare ölçüsünü oku (dikey mi, ne kadar geniş) */
function probeStream(cs){
  return navigator.mediaDevices.getUserMedia(cs).then(function(st){
    return new Promise(function(res){
      var v=$("#cam"),done=false,tr=st.getVideoTracks()[0];
      function fin(){if(done)return;done=true;var w=v.videoWidth||0,h=v.videoHeight||0,sg={};try{sg=tr.getSettings()||{}}catch(e){}
        res({st:st,tr:tr,w:w,h:h,fps:Math.round(sg.frameRate||0),sw:sg.width||0,sh:sg.height||0})}
      v.onloadedmetadata=function(){setTimeout(fin,120)};
      v.srcObject=st;v.play&&v.play().catch(function(){});
      setTimeout(fin,1800);
    });
  });
}
function beginRec(){
  mesgul=true;go("rec");
  $("#count").textContent="";$("#recBadge").style.display="none";
  var fm=(S.kamera==="environment")?"environment":"user",wide=(S.kadraj!=="standart");
  $("#cam").classList.toggle("mirror",fm==="user"); /* ön kamera önizlemesi ayna gibi; kayıt aynalanmaz */
  $("#cam").style.objectFit="cover"; /* önizleme tam ekran */
  var cands=camCands(fm,wide),key=fm+"|"+(wide?"w":"s"),log=[],best=null,i=0;
  var pick=(S.camPick&&S.camPick[key]);
  if(typeof pick==="number"&&pick>=0&&pick<cands.length){cands=[cands[pick]].concat(cands.filter(function(_,j){return j!==pick}))}
  function stopIt(r){try{r.st.getTracks().forEach(function(t){t.stop()})}catch(e){}}
  function finish(r){
    stream=r.st;$("#cam").srcObject=r.st;
    try{var cap=r.tr.getCapabilities&&r.tr.getCapabilities();if(cap&&cap.zoom&&typeof cap.zoom.min==="number")r.tr.applyConstraints({advanced:[{zoom:cap.zoom.min}]}).catch(function(){})}catch(e){}
    window.B360.cam={w:r.w,h:r.h,fps:r.fps,cand:r.ci};
    S.lastCam=r.w+"×"+r.h+" @"+r.fps+"fps (aday "+(r.ci+1)+", "+(r.w<r.h?"dikey":"YATAY")+")";
    S.camLog=log.join(" | ");S.camPick=S.camPick||{};S.camPick[key]=r.ci;save();
    countdown(3);
  }
  function next(){
    if(i>=cands.length){
      if(best){finish(best);return}
      navigator.mediaDevices.getUserMedia({video:true,audio:false}).then(function(st){stream=st;$("#cam").srcObject=st;S.lastCam="genel kamera";save();countdown(3)})
        .catch(function(){recBusy=false;mesgul=false;alert("Kameraya erişilemedi. Safari'de kamera iznini kontrol et.");go("attract")});
      return;
    }
    var cs=cands[i],ci=i;i++;
    probeStream(cs).then(function(r){
      r.ci=ci;log.push((ci+1)+": "+r.w+"×"+r.h+" @"+r.fps);
      var portrait=r.w&&r.h&&r.h>r.w,ratio=r.w&&r.h?r.w/r.h:0;
      if(!wide){finish(r);return}
      if(portrait&&ratio>=0.7){finish(r);return}          /* dikey ve geniş (3:4) → istediğimiz */
      if(portrait&&(!best||ratio>best.w/best.h)){if(best)stopIt(best);best=r}else stopIt(r); /* dikey ama dar: yedek */
      next();
    }).catch(function(e){log.push((ci+1)+": hata");next()});
  }
  next();
}
var AC=null;
function bip(hz,ms){ /* saha gürültülü — misafir başlangıcı DUYSUN */
  if(!S.sesli)return;
  try{
    AC=AC||new (window.AudioContext||window.webkitAudioContext)();
    if(AC.state==="suspended")AC.resume();
    var o=AC.createOscillator(),g=AC.createGain();
    o.type="sine";o.frequency.value=hz;g.gain.value=0.0001;
    o.connect(g);g.connect(AC.destination);o.start();
    g.gain.exponentialRampToValueAtTime(0.25,AC.currentTime+0.01);
    g.gain.exponentialRampToValueAtTime(0.0001,AC.currentTime+ms/1000);
    o.stop(AC.currentTime+ms/1000+0.02);
  }catch(e){}
}
function titre(p){try{navigator.vibrate&&navigator.vibrate(p)}catch(e){}}
function countdown(n){
  var y=$("#recHint");if(y)y.textContent=S.yonerge||"";
  if(n>0){$("#count").textContent=n;bip(660,120);titre(40);setTimeout(function(){countdown(n-1)},1000);return}
  $("#count").textContent="";bip(1040,260);titre([0,90,60,90]);
  if(y)y.textContent="";
  startRecording();
}
function pickMime(){
  var list=["video/mp4;codecs=avc1","video/mp4","video/webm;codecs=vp9","video/webm"];
  for(var i=0;i<list.length;i++){try{if(MediaRecorder.isTypeSupported(list[i]))return list[i]}catch(e){}}
  return "";
}
function startRecording(){
  chunks=[];
  var mt=pickMime();
  try{rec=mt?new MediaRecorder(stream,{mimeType:mt,videoBitsPerSecond:8000000}):new MediaRecorder(stream)}
  catch(e){rec=new MediaRecorder(stream)}
  var bitti=false;
  function bitir(){ /* tek sefer çalışır: onstop gelmezse bile yüklemeye geçer */
    if(bitti)return;bitti=true;clearTimeout(recWatch);clearInterval(recTimer);
    stopCam();
    bip(520,200);titre(120);
    if(!chunks.length){recBusy=false;mesgul=false;$("#upNote").textContent="Kayıt alınamadı — tekrar dene.";go("upload");setTimeout(function(){go("attract")},2500);return}
    if(!S.deneme)sayacArt("cekim");uploadVideo();
  }
  rec.ondataavailable=function(e){if(e.data&&e.data.size)chunks.push(e.data)};
  rec.onstop=bitir;
  rec.onerror=function(){try{rec.stop()}catch(e){}setTimeout(bitir,400)};
  try{rec.start(500)}catch(e){bitir();return}
  var left=S.sure;
  $("#recBadge").style.display="inline-flex";
  $("#recLeft").textContent="KAYIT · "+left+" sn";
  recTimer=setInterval(function(){
    left--;
    $("#recLeft").textContent="KAYIT · "+Math.max(0,left)+" sn";
    if(left<=0){clearInterval(recTimer);try{rec.stop()}catch(e){bitir()}}
  },1000);
  recWatch=setTimeout(bitir,(S.sure+6)*1000); /* güvenlik ağı: kayıt takılırsa yine de devam */
}
function stopCam(){
  try{if(stream)stream.getTracks().forEach(function(t){t.stop()})}catch(e){}
  stream=null;$("#cam").srcObject=null;
}
function keepBlob(blob){try{if(lastBlobUrl)URL.revokeObjectURL(lastBlobUrl)}catch(e){}try{lastBlobUrl=URL.createObjectURL(blob)}catch(e){lastBlobUrl=""}}

/* ---------- YÜKLEME ---------- */
var curVid=null; /* {pid,ver,dur} */
var bekleyen=null;   /* yüklenemeyen video burada durur — KAYBOLMAZ */
function uploadVideo(blobIn,deneme){
  go("upload");
  var blob=blobIn||new Blob(chunks,{type:chunks[0]?chunks[0].type:"video/webm"});
  bekleyen=blob;deneme=deneme||1;
  chunks=[];                                   /* bellek şişmesin */
  keepBlob(blob);
  $("#upNote").textContent="Video buluta yükleniyor…"+(deneme>1?(" (deneme "+deneme+")"):"");
  $("#upBar").style.width="10%";$("#upTekrar").hidden=true;
  var kls=S.deneme?"booth360/_deneme":("booth360/"+evSlug());
  cldUpload(blob,"video",{folder:kls,tags:(S.deneme?"deneme-360":(evSlug()+"-360"))},function(p){$("#upBar").style.width=Math.round(10+80*p)+"%"})
    .then(function(j){
      bekleyen=null;
      curVid={pid:j.public_id,ver:j.version,dur:+j.duration||S.sure};
      $("#upBar").style.width="100%";mesgul=false;recBusy=false;
      if(paketOf()==="editsiz"){ /* editsiz: şablon yok, ham video doğrudan karekoda */
        selTpl={id:"ham",n:"Ham video",e:"🎥"};
        lastUrl=tplUrl("ham");lastPage=pageUrl("ham");
        $("#doneNote").textContent=S.qrMod==="mp4"?"Kamerayı karekoda tut, videon telefonuna insin.":"Kamerayı karekoda tut — sayfa açılır: izle, kaydet, paylaş.";
        if(!S.deneme)sayacArt("teslim");drawQR(S.qrMod==="mp4"?lastUrl:lastPage);go("done");return;
      }
      muzikAcik=!!(S.muzikSec||Object.keys(S.tplMusic).length);
      if(S.warm)warm(activeTpls()[0].id);
      buildStyleGrid();go("style");
    }).catch(function(e){upFail((e&&e.message)||"yanıt okunamadı",deneme)});
}
function upFail(m,deneme){
  if(deneme<3){ /* internet bir an gittiyse kendi kendine tekrar dener */
    $("#upNote").textContent="Bağlantı sorunu ("+m+") — "+(deneme*4)+" sn sonra tekrar denenecek…";
    setTimeout(function(){uploadVideo(bekleyen,deneme+1)},deneme*4000);
    return;
  }
  mesgul=false;recBusy=false;
  $("#upNote").textContent="Yüklenemedi: "+m+". Video telefonda duruyor — internet gelince Tekrar dene'ye bas.";
  $("#upBar").style.width="0%";$("#upTekrar").hidden=false;
}
$("#upTekrarBtn").onclick=function(){if(bekleyen)uploadVideo(bekleyen,1)};
$("#upVazgec").onclick=function(){bekleyen=null;mesgul=false;recBusy=false;go("attract")};

/* ---------- ŞABLON → SPEC → URL ---------- */
var muzikAcik=false,selTpl=null,lastUrl="",lastPage="";
function mkSpec(tid,vid){
  var v=vid||curVid;if(!v)return null;
  if(tid==="ham")return {c:S.cldName,p:v.pid,v:v.ver,t:"ham",d:v.dur,
    l:logoVar()?S.logoPid:"",lp:S.logoPoz,lw:S.logoW,
    k:logoVar()?kKodu():"",              /* logo basılmıyorsa videoya hiç dokunulmaz */
    o:Object.assign({},S.flags,{logo:1})};
  return {c:S.cldName,p:v.pid,v:v.ver,t:tid,d:v.dur,f:S.yuzSn,r:S.turSn,
    l:S.logoPid||"",lp:S.logoPoz,lw:S.logoW,m:muzikAcik?musicFor(tid):"",
    x:fxOk(tid)?S.fxMode:"off",fp:S.fxPath,k:kKodu(),o:Object.assign({},S.flags,{tol:S.fxTol})};
}
/* FX varlıkları bulutta var mı? (başka cihazdan yüklenmiş olabilir) — HEAD ile yoklanır, S.fxHave'e yazılır */
function fxProbe(cb){
  var ids=["yildiz","kalp","konfeti","sparkle"],left=ids.length,ch=false;
  ids.forEach(function(id){
    var u="https://res.cloudinary.com/"+encodeURIComponent(S.cldName)+"/video/upload/"+S.fxPath+"/"+id+".mp4";
    fetch(u,{method:"HEAD",cache:"no-store"}).then(function(r){if(r.status===200&&!S.fxHave[id]){S.fxHave[id]=S.fxPath+"/"+id;ch=true}}).catch(function(){}).then(function(){if(--left===0){if(ch)save();if(cb)cb(ch)}});
  });
}
try{fxProbe()}catch(e){}
/* FX videosu yüklü değilse o şablon FX'siz kurulur (render kırılmasın) */
function fxOk(tid){
  if(paketOf()!=="efektli")return false; /* efektsiz paket: FX katmanı hiç eklenmez */
  var t=E.byId(tid);if(!t.fx||S.fxMode==="off")return false;
  var key=S.fxMode==="alpha"?(t.fx+"_a"):t.fx;return !!(S.fxHave&&S.fxHave[key]);
}
function tplUrl(tid,vid){var sp=mkSpec(tid,vid);return sp?E.url(sp):""}
function pageUrl(tid,vid){var sp=mkSpec(tid,vid);return sp?(pageBase()+"v.html#"+E.encode(sp)):""}
function warm(tid){var u=tplUrl(tid);if(!u)return;try{var sp=mkSpec(tid);maliyetEkle(u,(sp&&tid!=="ham")?E.plan(sp).out:0)}catch(e){}
  try{fetch(u,{method:"HEAD",cache:"no-store"}).catch(function(){})}catch(e){}}
/* Cloudinary "hazırlanıyor" (423) yoklaması */
function ready(url,onStat){
  return new Promise(function(res,rej){
    var t0=Date.now(),n=0;
    (function tick(){
      n++;if(onStat)onStat(n,Math.round((Date.now()-t0)/1000));
      var p;try{p=fetch(url,{method:"HEAD",cache:"no-store"})}catch(e){p=Promise.reject(e)}
      p.then(function(r){
        if(r.status===200||r.status===206){res(r);return}
        if(r.status===423||r.status===425||r.status===429||r.status>=500){retry();return}
        rej(new Error("HTTP "+r.status));
      }).catch(function(){retry()});
      function retry(){if(Date.now()-t0>150000){rej(new Error("zaman aşımı"));return}setTimeout(tick,n<3?1500:3000)}
    })();
  });
}
function speedBar(sp){
  var a=E.bar(sp),h='<div class="sb">';
  a.forEach(function(s){h+='<i class="'+(s.rev?"rev":(s.flash?"flash":s.k))+'" style="width:'+Math.max(1.5,s.w*100)+'%"></i>'});
  return h+'</div>';
}
function buildStyleGrid(){
  var g=$("#styleGrid");g.innerHTML="";
  activeTpls().forEach(function(t){
    var sp=mkSpec(t.id),P=E.plan(sp);
    var c=document.createElement("button");c.className="stcard";c.setAttribute("data-tpl",t.id);
    c.innerHTML='<div class="e">'+t.e+'</div><div class="n">'+t.n+'</div><div class="d">'+t.d+'</div>'+speedBar(sp)+
      '<div class="t">≈'+Math.round(P.out)+' sn'+(sp.m?" · 🎵":"")+(sp.x!=="off"?" · FX":"")+'</div>';
    c.onclick=function(){openPreview(t)};
    g.appendChild(c);
  });
  if(S.hamKart!==0&&paketOf()!=="editsiz"){ /* misafir şablon seçmek zorunda kalmasın */
    var hc=document.createElement("button");hc.className="stcard";hc.setAttribute("data-tpl","ham");
    var hs=mkSpec("ham"),isl=hs&&E.hamIslem(hs);
    hc.innerHTML='<div class="e">🎬</div><div class="n">Şablonsuz</div>'+
      '<div class="d">Çekildiği gibi — efekt yok, en hızlısı</div>'+
      '<div class="sb"><i class="mid" style="width:100%"></i></div>'+
      '<div class="t">≈'+Math.round((curVid&&curVid.dur)||S.sure)+' sn'+(isl?" · logo":"")+'</div>';
    hc.onclick=function(){openPreview({id:"ham",n:"Şablonsuz",e:"🎬"})};
    g.appendChild(hc);
  }
  var mc=$("#muzikChip"),has=!!(S.muzikSec||Object.keys(S.tplMusic).length);
  mc.hidden=!has;
  mc.classList.toggle("on",muzikAcik);
  mc.textContent=muzikAcik?"🎵 Müzik: AÇIK":"🎵 Müzik: kapalı";
}
$("#muzikChip").onclick=function(){muzikAcik=!muzikAcik;buildStyleGrid()};
var prevTok=0;
function openPreview(t){
  selTpl=t;var tok=++prevTok;
  var sp=mkSpec(t.id),url=E.url(sp);lastUrl=url;
  maliyetEkle(url,(t.id==="ham")?(E.hamIslem(sp)?(+sp.d||0):0):E.plan(sp).out);
  $("#prevName").textContent=t.e+" "+t.n+(sp.m?" · 🎵":"");
  go("prev");
  var v=$("#prevVid"),busy=$("#prevBusy"),stat=$("#prevStat"),use=$("#useBtn");
  use.disabled=true;busy.style.display="flex";busy.querySelector(".lede").textContent="Edit hazırlanıyor…";stat.textContent="";
  v.removeAttribute("src");try{v.load()}catch(e){}
  ready(url,function(n,sec){if(tok!==prevTok)return;stat.textContent=sec+" sn"+(sec>=20?" · ilk hazırlık 30–60 sn sürebilir":"")}).then(function(){
    if(tok!==prevTok)return;
    var opened=false;function openIt(){if(tok!==prevTok||opened)return;opened=true;busy.style.display="none";use.disabled=false}
    v.onloadeddata=openIt;v.onloadedmetadata=openIt;
    v.onerror=function(){if(tok!==prevTok||opened)return;busy.querySelector(".lede").textContent="Önizleme oynatılamadı — yine de kullanabilirsin.";stat.textContent="";use.disabled=false};
    v.src=url;v.play&&v.play().catch(function(){});
    setTimeout(openIt,6000); /* iOS bazen veri yüklemez; hazır olan videoyu bekletme */
  }).catch(function(e){
    if(tok!==prevTok)return;
    busy.querySelector(".lede").textContent="Bu edit hazırlanamadı — başka şablon dene.";
    stat.textContent=(e&&e.message)||"";
  });
}
$("#otherBtn").onclick=function(){prevTok++;$("#prevVid").removeAttribute("src");try{$("#prevVid").load()}catch(e){}go("style")};
$("#useBtn").onclick=function(){
  if(!selTpl)return;
  lastUrl=tplUrl(selTpl.id);lastPage=pageUrl(selTpl.id);
  var q=S.qrMod==="mp4"?lastUrl:lastPage;
  $("#doneNote").textContent=S.qrMod==="mp4"?"Kamerayı karekoda tut, videon telefonuna insin.":"Kamerayı karekoda tut — sayfa açılır: izle, kaydet, paylaş.";
  if(!S.deneme)sayacArt("teslim");drawQR(q);
  go("done");
};
$("#yenidenBtn").onclick=function(){curVid=null;go("attract")};
$("#styleBasa").onclick=function(){curVid=null;go("attract")};
$("#prevBasa").onclick=function(){prevTok++;$("#prevVid").removeAttribute("src");try{$("#prevVid").load()}catch(e){}curVid=null;go("attract")};
$("#againBtn").onclick=function(){curVid=null;$("#prevVid").removeAttribute("src");go("attract")};
$("#qrKopya").onclick=function(){
  var t=$("#qrAdres").textContent||"",b=$("#qrKopya");
  try{navigator.clipboard.writeText(t).then(function(){b.textContent="Kopyalandı"},function(){})}catch(e){}
  setTimeout(function(){b.textContent="Bağlantıyı kopyala"},2500);
};
$("#qrAc").onclick=function(){var t=$("#qrAdres").textContent||"";if(t)window.open(t,"_blank")};

/* ---------- KALİBRASYON ---------- */
var calT1=-1,calT2=-1,calTimer=null;
function openCal(){
  if(!lastBlobUrl){alert("Önce bir deneme çekimi yap ya da 'Video dosyasıyla' seç.");return}
  calT1=-1;calT2=-1;
  var v=$("#calVid");v.src=lastBlobUrl;v.currentTime=0;v.play&&v.play().catch(function(){});
  clearInterval(calTimer);calTimer=setInterval(function(){$("#calTime").textContent=(v.currentTime||0).toFixed(1)},100);
  calVals();go("cal");
}
function calVals(){
  var h="";
  if(calT1>=0)h+="İlk yüz anı: <b>"+calT1.toFixed(1)+" sn</b>";else h+="İlk yüz anı: —";
  h+="<br>";
  if(calT2>=0)h+="Tur süresi: <b>"+(calT2-calT1).toFixed(1)+" sn</b>";else h+="Tur süresi: —"+(calT1>=0?" (ikinci kez öne gelince bas)":"");
  $("#calVals").innerHTML=h;
  $("#calFace").textContent=calT1<0?"YÜZ TAM ÖNDE":(calT2<0?"YÜZ TEKRAR ÖNDE":"TAMAM");
}
$("#calBtn").onclick=openCal;
$("#calFileBtn").onclick=function(){$("#calFile").click()};
$("#calFile").addEventListener("change",function(){var f=this.files&&this.files[0];this.value="";if(!f)return;keepBlob(f);openCal()});
$("#calFace").onclick=function(){
  var t=$("#calVid").currentTime||0;
  if(calT1<0){calT1=t}else if(calT2<0){if(t-calT1>1.5)calT2=t;else{calT1=t}}
  calVals();
};
$("#calReset").onclick=function(){calT1=-1;calT2=-1;$("#calVid").currentTime=0;calVals()};
function closeCal(){clearInterval(calTimer);try{$("#calVid").pause()}catch(e){}fillAdmin();go("admin")}
$("#calSave").onclick=function(){
  if(calT1>=0)S.yuzSn=Math.round(calT1*10)/10;
  if(calT2>=0)S.turSn=Math.round((calT2-calT1)*10)/10;
  save();closeCal();
};
$("#calCancel").onclick=closeCal;

/* ---------- QR ---------- */
function drawQR(text){
  var cv=$("#qrCanvas"),x=cv.getContext("2d");
  x.fillStyle="#FFFFFF";x.fillRect(0,0,cv.width,cv.height); /* saf beyaz zemin — kamera kontrastı */
  var say=$("#qrAdres");if(say)say.textContent=text||"";
  var uy=$("#qrUyari");if(uy)uy.textContent=/^https?:\/\//i.test(text||"")?"":"UYARI: karekoddaki adres web adresi değil — Ayarlar → Site adresi alanını doldur.";
  try{
    var q=qrcode(0,"M");q.addData(text);q.make();
    var n=q.getModuleCount(),quiet=4;                       /* standart 4 modül sessiz alan */
    var cell=Math.floor(cv.width/(n+2*quiet));if(cell<1)cell=1;
    var off=Math.floor((cv.width-cell*n)/2);
    x.fillStyle="#000000";                                  /* saf siyah */
    for(var r=0;r<n;r++)for(var c=0;c<n;c++)if(q.isDark(r,c))x.fillRect(off+c*cell,off+r*cell,cell,cell);
    if(window.B360)window.B360.qrInfo={n:n,cell:cell,len:(text||"").length};
  }catch(e){
    x.fillStyle="#12100E";x.font="20px sans-serif";x.textAlign="center";
    x.fillText("QR hazırlanamadı",cv.width/2,cv.height/2);
  }
}

window.B360={VER:VER,S:S,save:save,evSlug:evSlug,E:E,mkSpec:mkSpec,tplUrl:tplUrl,pageUrl:pageUrl,ready:ready,go:go,
  setVid:function(v){curVid=v},muzik:function(a){muzikAcik=a},buildStyleGrid:buildStyleGrid,openPreview:openPreview,
  last:function(){return {url:lastUrl,page:lastPage}},fillAdmin:fillAdmin,keepBlob:keepBlob,openCal:openCal,
  galeriUrl:galeriUrl,raporUrl:raporUrl,sayacMetin:sayacMetin,bulutSayim:bulutSayim,paketOf:paketOf,pageBase:pageBase,
  maliyetMetin:maliyetMetin,ayarKod:ayarKod,ayarBag:ayarBag,ayarUygula:ayarUygula,snTl:snTl,PINK:PINK,kKodu:kKodu,logoVar:logoVar,applyBrand:applyBrand,
  tani:function(){return {ekran:cur,mesgul:mesgul,bekleyen:!!bekleyen,sayac:S.sayac||{},oto:+S.otoDon||0,ayarGeldi:AYAR_GELDI,deneme:!!S.deneme}}};
})();
