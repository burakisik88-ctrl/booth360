#!/bin/bash
cd "$(dirname "$0")/.."
T=0;G=0;FAIL=""
for f in test/t360v2.py test/t360saha.py test/t360ticari.py test/t360onkontrol.py test/t360marka.py test/qrtest.py; do
  out=$(timeout 600 python3 "$f" 2>&1)
  line=$(echo "$out" | grep "SONUÇ:")
  g=$(echo "$line"|sed -E 's/.*SONUÇ: ([0-9]+)\/([0-9]+).*/\1/');t=$(echo "$line"|sed -E 's/.*SONUÇ: ([0-9]+)\/([0-9]+).*/\2/')
  G=$((G+g));T=$((T+t))
  printf "%-26s %s\n" "$(basename $f)" "$line"
  [ "$g" != "$t" ] && FAIL="$FAIL $(basename $f)"
done
echo "──────────────────────────────────"
echo "TOPLAM: $G/$T${FAIL:+   DÜŞEN:$FAIL}"
