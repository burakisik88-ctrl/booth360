# Misafir GitHub adresini görmesin — 360.yopi.com.tr

**Sorun:** misafir karekodu okutunca Safari'nin üst çubuğunda
`burakisik88-ctrl.github.io` yazıyor. Kurumsal bir kongrede bu kötü duruyor.

**Çözüm:** GitHub Pages ücretsiz olarak kendi alan adınızla çalışır.
Sizde zaten **yopi.com.tr** var, yani yeni alan adı almanıza gerek yok —
bir alt alan adı açmak yeterli ve **bedava**.

Misafir şunu görür: **360.yopi.com.tr** — hem GitHub gizlenir hem marka görünür.

---

## 1) DNS kaydı (alan adını yönettiğiniz yerde)

yopi.com.tr'nin DNS panelinde (Natro / İsimtescil / GoDaddy — hangisiyse)
**tek bir CNAME kaydı** ekleyin:

| Alan | Değer |
|---|---|
| Tür | CNAME |
| Ad / Host | `360` |
| Hedef / Value | `burakisik88-ctrl.github.io` |
| TTL | 3600 (ya da otomatik) |

Not: hedefin sonuna nokta isteyen paneller var → `burakisik88-ctrl.github.io.`

## 2) GitHub tarafı

1. github.com/burakisik88-ctrl/booth360 → **Settings** → sol menüde **Pages**
2. **Custom domain** kutusuna `360.yopi.com.tr` yazın → **Save**
3. GitHub deponuza otomatik olarak `CNAME` adlı bir dosya ekler. Bu dosya silinmemeli.
   (Bundan sonra dosya yüklerken bu dosyayı da koruyun — sürükleyip bıraktığınız
   klasörde CNAME dosyası yoksa GitHub mevcut olanı silmez, sorun çıkmaz.)
4. DNS yayılınca (genelde 10–30 dakika, bazen birkaç saat) aynı sayfada
   **"Enforce HTTPS"** kutucuğu tıklanabilir hale gelir → işaretleyin.
   Bu kutu tıklanabilir olmadan misafire link vermeyin, sertifika hazır değildir.

## 3) Uygulama tarafı (siz yapmayın, ben yapacağım)

Panel → **Site adresi** alanına `https://360.yopi.com.tr/` yazılınca
karekodlar da yeni adresi gösterir. DNS aktif olduğunda söyleyin, ayar
bağlantısını yeni adresle üretip göndereyim.

---

## Ana ekrana ekleme (tarayıcı çubuğu gitsin)

v0.8.0 ile beş sayfaya da PWA dosyaları eklendi. Booth telefonunda:

1. Safari'de `https://360.yopi.com.tr/` (ya da şimdilik GitHub adresi) açın
2. Alttaki **Paylaş** simgesi → **Ana Ekrana Ekle**
3. Ana ekrandaki OBSKURA 360 simgesinden açın → adres çubuğu ve alt butonlar yok,
   tam ekran, dikey kilitli çalışır

**Misafir için bu geçerli değil:** misafir karekodu okutup Safari'de açar,
ana ekrana eklemez. Onun gördüğü adresi düzelten tek şey 1. ve 2. adımdaki
alan adıdır.
