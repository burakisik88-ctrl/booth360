#!/bin/bash
# OBSKURA 360 — tüm test takımı.
# Çöken ya da eksik bir test artık SESSİZCE GEÇMİŞ SAYILMIYOR (20 Eyl 2026):
# SONUÇ satırı olmayan dosya DÜŞEN listesine girer ve çıkış kodu 1 olur.
cd "$(dirname "$0")/.."
[ -f test/tiny.mp4 ] || { echo "EKSİK: test/tiny.mp4 (testlerin deneme videosu) — takım çalıştırılamaz."; exit 1; }
T=0;G=0;FAIL="";YOK=""
for f in test/t360v2.py test/t360saha.py test/t360ticari.py test/t360onkontrol.py test/t360marka.py test/t360ayrim.py test/t360kalite.py test/t360bant.py test/t360saha2.py test/t360bantgorsel.py test/t360bantparca.py test/qrtest.py; do
  b=$(basename "$f")
  if [ ! -f "$f" ]; then printf "%-26s %s\n" "$b" "DOSYA YOK"; YOK="$YOK $b"; continue; fi
  out=$(timeout 600 python3 "$f" 2>&1)
  line=$(echo "$out" | grep "SONUÇ:")
  if [ -z "$line" ]; then
    printf "%-26s %s\n" "$b" "ÇÖKTÜ → $(echo "$out" | tail -1 | cut -c1-70)"
    FAIL="$FAIL $b"; continue
  fi
  g=$(echo "$line"|sed -E 's/.*SONUÇ: ([0-9]+)\/([0-9]+).*/\1/');t=$(echo "$line"|sed -E 's/.*SONUÇ: ([0-9]+)\/([0-9]+).*/\2/')
  G=$((G+g));T=$((T+t))
  printf "%-26s %s\n" "$b" "$line"
  [ "$g" != "$t" ] && FAIL="$FAIL $b"
done
echo "──────────────────────────────────"
echo "TOPLAM: $G/$T${FAIL:+   DÜŞEN:$FAIL}${YOK:+   DOSYA YOK:$YOK}"
[ -z "$FAIL$YOK" ] || exit 1
exit 0
