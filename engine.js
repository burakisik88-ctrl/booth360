/* OBSKURA 360 — Şablon Motoru v0.2 (index.html ve v.html'e aynen gömülür)
   Şablon = hız eğrisi (segmentler) + FX katmanı + renk + logo + müzik.
   Motor, şablonu Cloudinary dönüşüm zincirine çevirir; ileride FFmpeg'e de çevrilebilir. */
var B360E=(function(){
"use strict";
function r2(x){return Math.round(x*100)/100}
function lid(p){return String(p).replace(/\//g,":")}
var DEFO={zoom:1,flash:1,dbl:1,noise:0,du:1,logo:1,fx:1,music:1,renk:1,bant:1,tol:25};
var POS={ne:"g_north_east,x_0.04,y_0.03",nw:"g_north_west,x_0.04,y_0.03",se:"g_south_east,x_0.04,y_0.04",sw:"g_south_west,x_0.04,y_0.04",s:"g_south,y_0.04",n:"g_north,y_0.03"};

/* ---- ŞABLONLAR ----
   w(D,F): D=kaynak süresi (sn), F=yüz anı (sn). Segment: {s,e,r,dbl,x}
   r = e_accelerate (-50 yarı hız … 100 iki kat), dbl=1 → ikinci -50 (¼×), x: "rev" | "flash" | "zoom" */
var TEMPLATES=[
 {id:"yildiz",n:"Yıldız Yağmuru",e:"✨",d:"Yavaş giriş, hızlı tur, yüzünde ağır çekim — yıldızlar yağar",fx:"yildiz",grade:"e_saturation:15/e_contrast:6",
  w:function(D,F){return[{s:0,e:1.5,r:-50},{s:1.5,e:F-0.7,r:100},{s:F-0.7,e:F+0.9,r:-50,dbl:1},{s:F+0.9,e:D-2,r:100},{s:D-2,e:D,r:-50}]}},
 {id:"kalp",n:"Kalp Kalbe",e:"💗",d:"Yumuşak giriş, yüzünde kalpler ve ağır çekim, hızlı çıkış",fx:"kalp",grade:"e_saturation:10/e_brightness:4",
  w:function(D,F){return[{s:0,e:2,r:-50},{s:2,e:F-0.8,r:0},{s:F-0.8,e:F+1,r:-50,dbl:1},{s:F+1,e:D,r:100}]}},
 {id:"konfeti",n:"Konfeti Patlaması",e:"🎉",d:"Hızlı giriş, flaş, ağır çekim vurgu, geri sarımlı final",fx:"konfeti",grade:"e_saturation:25/e_contrast:8",
  w:function(D,F){return[{s:0,e:F-1,r:60},{s:F-1,e:F-0.88,r:0,x:"flash"},{s:F-0.88,e:F+1,r:-50},{s:F+1,e:D,r:60},{s:D-3,e:D,r:100,x:"rev"}]}},
 {id:"noir",n:"Sinema Noir",e:"🎩",d:"Siyah-beyaz, uzun ağır çekim yüz anı, hızlı tur, yavaş kapanış",fx:"",grade:"e_grayscale/e_contrast:18",noise:10,
  w:function(D,F){return[{s:0,e:F-1.2,r:0},{s:F-1.2,e:F+1.4,r:-50},{s:F+1.4,e:D-2,r:100},{s:D-2,e:D,r:-50}]}},
 {id:"geri",n:"Geri Sarım Pro",e:"⏪",d:"Hızlı tur, yüzünde ağır çekim, bütün tur tersten, son bir yüz anı",fx:"sparkle",grade:"e_saturation:30/e_contrast:10",
  w:function(D,F){return[{s:0,e:F-0.6,r:100},{s:F-0.6,e:F+0.8,r:-50},{s:F+0.8,e:D,r:100},{s:0,e:D,r:100,x:"rev"},{s:F-0.6,e:F+0.8,r:-50,free:1}]}},
 {id:"kulup",n:"Kulüp",e:"🪩",d:"Zoom vuruşları, ¼× yüz anı, strobe flaşlar, hızlı çıkış",fx:"sparkle",grade:"e_contrast:20/e_saturation:20",
  w:function(D,F){var a=[],t=0,i;
    for(i=0;i<3&&t+2.4<F-0.5;i++){a.push({s:t,e:t+1.8,r:60});a.push({s:t+1.8,e:t+2.4,r:60,x:"zoom"});t+=2.4}
    a.push({s:t,e:F-0.5,r:60});a.push({s:F-0.5,e:F+0.7,r:-50,dbl:1});
    t=F+0.7;for(i=0;i<2;i++){a.push({s:t,e:t+0.1,r:0,x:"flash"});a.push({s:t+0.1,e:t+0.5,r:100});t+=0.5}
    a.push({s:t,e:D,r:100});return a}}
];
function byId(id){for(var i=0;i<TEMPLATES.length;i++)if(TEMPLATES[i].id===id)return TEMPLATES[i];return TEMPLATES[0]}

/* yüz anı: kol misafirin önünden başlar; yüz f0 + k*tur anlarında öne gelir */
function facePick(D,f0,tur){
  f0=+f0||0;tur=+tur||10;if(tur<2)tur=2;
  var c=[],k=0,t;
  while((t=f0+k*tur)<D&&k<50){c.push(t);k++}
  var lo=Math.min(2.5,D*0.3),hi=D-2;
  for(var i=0;i<c.length;i++)if(c[i]>=lo&&c[i]<=hi)return r2(c[i]);
  for(i=0;i<c.length;i++)if(c[i]>1.5&&c[i]<D-1.5)return r2(c[i]);
  return r2(D/2);
}
/* segmentleri kırp, sırala, boşluk bırakma (ters segmentler ayrı sayılır) */
function norm(ws,D){
  var out=[],prevEnd=0;
  for(var i=0;i<ws.length;i++){
    var w=ws[i],s=Math.max(0,Math.min(D,+w.s)),e=Math.max(0,Math.min(D,+w.e));
    if(w.x==="rev"||w.free){ /* ters/tekrar parçalar akış sırasına bağlı değil */
      if(e-s>=0.3)out.push({s:r2(s),e:r2(e),r:w.r||0,dbl:w.dbl?1:0,x:w.x||""});
      continue;
    }
    if(s<prevEnd)s=prevEnd;
    if(e-s<0.08)continue;
    out.push({s:r2(s),e:r2(e),r:w.r||0,dbl:w.dbl?1:0,x:w.x||""});
    prevEnd=e;
  }
  return out;
}
function fac(sg,o){var f=1+(sg.r||0)/100;if(sg.dbl&&o.dbl)f*=0.5;return f}
function outDur(segs,o){var t=0;for(var i=0;i<segs.length;i++)t+=(segs[i].e-segs[i].s)/fac(segs[i],o);return r2(t)}
function segComps(sg,o,idx){
  var c=[],base="so_"+r2(sg.s)+",eo_"+r2(sg.e);
  if(sg.r)base+=",e_accelerate:"+sg.r;
  c.push(base);
  if(sg.x==="rev")c.push("e_reverse");
  if(sg.x==="flash"&&o.flash)c.push("e_brightness:90");
  if(sg.dbl&&o.dbl)c.push("e_accelerate:-50");
  if(sg.x==="zoom"&&o.zoom&&idx>0){c.push("c_crop,w_0.85,h_0.85,g_center");c.push("c_scale,w_1.0,h_1.0,fl_relative")}
  return c;
}
function flagsOf(spec){var o=Object.assign({},DEFO);if(spec.o)Object.keys(spec.o).forEach(function(k){o[k]=spec.o[k]});return o}
function plan(spec){
  var tpl=byId(spec.t),o=flagsOf(spec),D=+spec.d||15;if(D<3)D=3;
  var F=facePick(D,spec.f,spec.r),segs=norm(tpl.w(D,F),D);
  return {tpl:tpl,o:o,D:D,F:F,segs:segs,out:outDur(segs,o)};
}
/* geniş (3:4) kaynağı 9:16'ya oturtma yolu:
   g916  = bulanık bant (eski varsayılan — bant çok baskın oluyordu)
   g916d = düz koyu bant, logo yeri kalır ama ekranı kesmez  ← varsayılan
   g916k = bant yok, kenarlardan kırpar (tam ekran) */
/* ---- BANT GEOMETRİSİ ----
   Bant, 9:16 tuvale oturmayan görüntünün yanında kalan koyu şerittir.
   Ne kadar DAR bant istenirse görüntü o kadar çok kenardan kırpılır — takas budur:
     bant 240 px → içerik 1080×1440 (3:4, en geniş kadraj)
     bant 170 px → içerik 1080×1580
     bant 120 px → içerik 1080×1680
     bantsız     → içerik 1080×1920 (tam ekran, kenarlar en çok kırpılır)
   Düzen: ikisi (üst+alt eşit) · alt (içerik yukarı yaslanır) · üst · yok.
   Tek bantta şerit seçilen yükseklikte kalır, iki katına çıkmaz. */
function bantGeo(spec){
  var yer=spec.bp||"ikisi", h=Math.max(0,Math.min(400,+spec.bh||0));
  if(yer==="yok"||!h)return {yer:"yok",h:0,ic:1920};
  var ic=(yer==="ikisi")?(1920-2*h):(1920-h);
  return {yer:yer,h:h,ic:Math.max(600,ic)};
}
function kadraj(k,spec){
  /* yeni yol: bant ayarları verilmişse geometri onlardan kurulur */
  if(spec&&spec.bh!==undefined&&spec.bp){
    var g=bantGeo(spec);
    var zemin=(spec.bb==="blur")?"b_blurred:400:15":("b_rgb:"+(String(spec.bb||"0D0B0A").replace(/^#/,"").replace(/[^0-9A-Fa-f]/g,"")||"0D0B0A"));
    if(g.yer==="yok")return "c_fill,w_1080,h_1920,g_center";
    var yer=(g.yer==="alt")?",g_north":((g.yer==="ust")?",g_south":"");
    return "c_fill,w_1080,h_"+g.ic+",g_center/c_pad,w_1080,h_1920"+yer+","+zemin;
  }
  /* eski kurulumlar bozulmasın */
  if(k==="g916")return "c_pad,w_1080,h_1920,b_blurred:400:15";
  if(k==="g916d")return "c_pad,w_1080,h_1920,b_rgb:0D0B0A";
  if(k==="g916k")return "c_fill,w_1080,h_1920,g_center";
  return "";
}
/* ---- BANT YAZISI ----
   Kadraj 3:4 kareyi 9:16'ya oturtunca alt-ustte 240'ar piksel bant kaliyor.
   Etkinlik adi oraya basiliyor; her indirilen videoda gorunuyor.
   Cloudinary metin katmani: l_text:<font>_<boy>_bold:<metin>,co_rgb:...
   Metin URL-encode edilir; "," ve "/" URL yapisini bozdugu icin CIFT encode sart. */
function txtEnc(t){
  var e=encodeURIComponent(String(t||"").trim());
  return e.replace(/%2C/gi,"%252C").replace(/%2F/gi,"%252F");
}
function bantKat(metin,spec,yon){
  var t=txtEnc(metin);if(!t)return [];
  var font=(spec.bf||"Montserrat").replace(/[^A-Za-z0-9 ]/g,"").replace(/ /g,"%20");
  var boy=Math.max(18,Math.min(120,+spec.bs||46));
  var renk=String(spec.bc||"F3EDE4").replace(/^#/,"").replace(/[^0-9A-Fa-f]/g,"")||"F3EDE4";
  /* YAZIYI BANDA ORTALA: bant yüksekliği ve punto biliniyorsa y hesaplanır.
     Montserrat/benzeri bold'da görünen harf yüksekliği ≈ 0.72 × punto.
     y = (bant - harfYüksekliği) / 2 → şerit içinde ortalı durur. */
  var g=bantGeo(spec), bandH=g.h;
  /* tek bantta metin o şeride gider; iki bantta her ikisi de aynı yükseklikte */
  var y;
  if(bandH>0){
    var harf=Math.round(0.72*boy);
    y=Math.round((bandH-harf)/2);
    y=Math.max(4,Math.min(bandH-harf-2,y));
    if(!isFinite(y)||y<0)y=Math.round(bandH*0.25);
  }else{
    y=Math.max(0,Math.min(400,+spec.by||60));   /* bantsız: görüntünün üstünde, kenardan */
  }
  y=Math.max(0,y+(+spec.bo||0));                /* ince ayar: yukarı/aşağı kaydır */
  /* c_fit,w_940 → uzun kongre adi kesilmez, iki satira sarar. _center → satirlar ortalanir.
     Canlida dogrulandi (16 Eyl 2026, Turkce harfler dahil). */
  return ["l_text:"+font+"_"+boy+"_bold_center:"+t+",co_rgb:"+renk+",c_fit,w_940",
          "fl_layer_apply,g_"+(yon==="ust"?"north":"south")+",y_"+y];
}
/* ---- BANT GÖRSELİ ----
   Tasarımcının hazırladığı 1080×240 şerit, bandın tamamını kaplar.
   Yazı katmanı yerine geçer: görsel varsa o yöndeki l_text basılmaz.
   c_fill → şerit bant yüksekliğine birebir oturur, orantı bozulmaz. */
function bantGorsel(pid,spec,yon){
  pid=String(pid||"").trim(); if(!pid)return [];
  var g=bantGeo(spec), h=g.h||240;
  return ["l_"+lid(pid),"c_fill,w_1080,h_"+h,
          "fl_layer_apply,g_"+(yon==="ust"?"north":"south")];
}
function bantKatmani(spec,yon){
  if(!bantYonOk(spec,yon))return [];
  var gor=(yon==="ust")?spec.bgu:spec.bga;
  if(gor&&String(gor).trim())return bantGorsel(gor,spec,yon);
  var mt=(yon==="ust")?spec.bu:spec.ba;
  return (mt&&String(mt).trim())?bantKat(mt,spec,yon):[];
}
/* ---- LOGO KATMANI ----
   Normal konumlar köşe/kenar damgasıdır: c_scale ile tuval genişliğine oranlanır.
   "balt"/"bust" = logoyu BANDIN İÇİNE ortalar:
     c_fit  → logo bant iç yüksekliğine ve seçilen genişliğe sığdırılır
     c_pad  → tam bant ölçüsünde saydam kutuya ortalanır
     g_south/g_north, y_0 → kutu bandın üstüne birebir oturur. */
function logoKat(spec,o){
  if(!(o.logo&&spec.l))return [];
  var W=(+spec.lw||0.22), pid=lid(spec.l), lp=spec.lp||"ne";
  /* "dalt"/"dust" = TEK PARÇA ŞERİT: logo dosyası bandın tamamını kaplar.
     Burak: "sen benim yüklediğimi tek logo olarak düşün" — iki kurum logosu ve
     etkinlik adı tek dosyada geliyor, kenarda boşluk kalmamalı. */
  if(lp==="dalt"||lp==="dust"){
    var gd=bantGeo(spec), yond=(lp==="dust")?"ust":"alt";
    if(gd.h>0&&bantYonOk(spec,yond))return bantGorsel(spec.l,spec,yond);
    lp=(lp==="dust")?"n":"s";
  }
  if(lp==="balt"||lp==="bust"){
    var g=bantGeo(spec);
    if(g.h>0&&bantYonOk(spec,lp==="bust"?"ust":"alt")){
      var px=Math.round(W*1080), ic=Math.max(20,g.h-28);
      return ["l_"+pid,"c_fit,w_"+px+",h_"+ic,
              "c_pad,w_"+px+",h_"+g.h+",b_transparent",
              "fl_layer_apply,g_"+(lp==="bust"?"north":"south")];
    }
    lp=(lp==="bust")?"n":"s";   /* bant yoksa kenara düşer */
  }
  return ["l_"+pid,"c_scale,w_"+W+",fl_relative","fl_layer_apply,"+(POS[lp]||POS.ne)];
}
function bantYonOk(spec,yon){
  var yer=spec.bp||"ikisi";
  if(yer==="ikisi"||yer==="yok")return true;
  return (yer==="alt"&&yon==="alt")||(yer==="ust"&&yon==="ust");
}
function bantVar(spec){var o=flagsOf(spec);return !!(o.bant&&((spec.bu&&String(spec.bu).trim())||(spec.ba&&String(spec.ba).trim())||(spec.bgu&&String(spec.bgu).trim())||(spec.bga&&String(spec.bga).trim())))}
function chain(spec){
  var P=plan(spec),o=P.o,tpl=P.tpl,L=lid(spec.p),parts=[];
  P.segs.forEach(function(sg,i){
    var cs=segComps(sg,o,i);
    if(i===0)parts=parts.concat(cs);
    else{cs[0]="l_video:"+L+","+cs[0]+",fl_splice";parts=parts.concat(cs);parts.push("fl_layer_apply")} /* fl_splice l_video bileşeninin İÇİNDE olmalı — canlıda doğrulandı (5 Eyl 2026) */
  });
  var du=o.du?(",du_"+r2(P.out+0.5)):"";
  var kp=kadraj(spec.k,spec);if(kp)parts.push(kp);
  if(o.fx&&tpl.fx&&spec.x&&spec.x!=="off"){
    var fp=lid(spec.fp||"booth360/_fx");
    if(spec.x==="alpha"){parts.push("l_video:"+fp+":"+tpl.fx+"_a"+du);parts.push("c_scale,w_1.0,fl_relative")}
    else{parts.push("l_video:"+fp+":"+tpl.fx+du);parts.push("c_scale,w_1.0,fl_relative");parts.push("e_make_transparent:"+(o.tol||25)+",co_rgb:00ff00")}
    parts.push("fl_layer_apply");
  }
  if(o.renk&&tpl.grade)parts.push(tpl.grade);   /* renk filtresi de kapatilabilir olmali */
  if(o.noise&&tpl.noise)parts.push("e_noise:"+tpl.noise);
  parts=parts.concat(logoKat(spec,o));
  if(o.bant){
    parts=parts.concat(bantKatmani(spec,"ust"));
    parts=parts.concat(bantKatmani(spec,"alt"));
  }
  if(o.music&&spec.m){parts.push("l_audio:"+lid(spec.m)+du);parts.push("fl_layer_apply")} /* ses katmanı l_audio: ile — l_video mp3'ü sessizce atıyordu */
  parts.push("q_auto");
  return parts.join("/");
}
/* ŞABLONSUZ: logo zorunlu değilse hiç bulut işlemi yok (sıfır kredi, anında hazır).
   Logo zorunluysa yalnız kadraj + logo basılır — şablon, efekt, müzik yok. */
function hamChain(spec){
  var parts=[],kp=kadraj(spec.k,spec),o=flagsOf(spec);
  if(kp)parts.push(kp);
  parts=parts.concat(logoKat(spec,o));
  if(o.bant){
    parts=parts.concat(bantKatmani(spec,"ust"));
    parts=parts.concat(bantKatmani(spec,"alt"));
  }
  parts.push("q_auto");
  return parts.join("/");
}
function hamIslem(spec){var o=flagsOf(spec);
  return !!(spec.t==="ham"&&((o.logo&&spec.l)||bantVar(spec)))}
function url(spec){
  var base="https://res.cloudinary.com/"+encodeURIComponent(spec.c||"")+"/video/upload/";
  if(spec.t==="ham"){
    if(hamIslem(spec))return base+hamChain(spec)+"/v"+(spec.v||1)+"/"+spec.p+".mp4";
    return base+"v"+(spec.v||1)+"/"+spec.p+".mp4"; /* dokunulmamış ham video */
  }
  return base+chain(spec)+"/v"+(spec.v||1)+"/"+spec.p+".mp4";
}
/* misafir kartı için hız şeridi: [{w:oran,k:slow|mid|fast,rev,flash}] */
function bar(spec){
  var P=plan(spec),tot=P.out||1,a=[];
  P.segs.forEach(function(sg){var f=fac(sg,P.o),d=(sg.e-sg.s)/f;
    a.push({w:d/tot,k:f<0.6?"slow":(f>1.2?"fast":"mid"),rev:sg.x==="rev",flash:sg.x==="flash"})});
  return a;
}
/* QR sayfası için kısa kodlama */
var FK={zoom:"z",flash:"f",dbl:"d",noise:"n",du:"u",logo:"l",fx:"x",music:"m",renk:"g",bant:"b"};
var KOK="booth360/";
var VARSAY={lp:"ne",lw:"0.22",bc:"F3EDE4",bs:"46",bf:"Montserrat",by:"92",bp:"ikisi",bb:"0D0B0A",bo:"0",fp:"booth360/_fx"};
function kis(k,v){ /* ortak klasör önekini at — karekod seyrek kalsın */
  return (k==="p"||k==="l"||k==="m"||k==="fp"||k==="bga"||k==="bgu")&&v.indexOf(KOK)===0 ? "~"+v.slice(KOK.length) : v;
}
function uzat(k,v){
  return (k==="p"||k==="l"||k==="m"||k==="fp"||k==="bga"||k==="bgu")&&v.charAt(0)==="~" ? KOK+v.slice(1) : v;
}
function encode(spec){
  var q=new URLSearchParams();
  ["c","p","v","t","d","f","r","l","lp","lw","m","x","fp","k","bu","ba","bc","bs","bf","by","bh","bp","bb","bo","bga","bgu"].forEach(function(k){
    if(spec[k]===undefined||spec[k]===""||spec[k]===null)return;
    var v=String(spec[k]);
    if(VARSAY[k]!==undefined&&v===VARSAY[k])return;   /* varsayılanı yazma */
    q.set(k,kis(k,v));
  });
  var o=flagsOf(spec),s="";Object.keys(FK).forEach(function(k){if(o[k])s+=FK[k]});
  q.set("o",s);q.set("tl",String(o.tol||25));
  return q.toString();
}
function decode(str){
  var q=new URLSearchParams(String(str||"").replace(/^#/,"")),spec={};
  ["c","p","v","t","d","f","r","l","lp","lw","m","x","fp","k","bu","ba","bc","bs","bf","by","bh","bp","bb","bo","bga","bgu"].forEach(function(k){
    spec[k]=q.has(k)?uzat(k,q.get(k)):VARSAY[k];
    if(spec[k]===undefined)delete spec[k];
  });
  var o={},s=q.get("o")||"";Object.keys(FK).forEach(function(k){o[k]=s.indexOf(FK[k])>=0?1:0});
  o.tol=+(q.get("tl")||25);spec.o=o;
  return spec;
}
return {TEMPLATES:TEMPLATES,byId:byId,plan:plan,chain:chain,url:url,bar:bar,encode:encode,decode:decode,facePick:facePick,DEFO:DEFO,lid:lid,hamIslem:hamIslem,kadraj:kadraj,bantKat:bantKat,bantVar:bantVar,txtEnc:txtEnc,bantGeo:bantGeo,bantYonOk:bantYonOk};
})();
