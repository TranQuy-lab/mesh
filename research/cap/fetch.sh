#!/bin/bash
# usage: fetch.sh <name> <url>
n="$1"; u="$2"; d=/home/noble-tran/AIforlife/research/cap/src
code=$(curl -sSL -m 70 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36" -o "$d/$n.raw" -w "%{http_code}" "$u")
echo "[$code] $n  <= $u"
if [ "$code" = "200" ]; then
python3 - "$d/$n.raw" "$d/$n.txt" <<'PY'
import re,html,sys
raw=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
t=re.sub(r'<(script|style|nav|header|footer).*?</\1>','',raw,flags=re.S|re.I)
t=re.sub(r'<[^>]+>',' ',t)
t=re.sub(r'[ \t]+',' ',html.unescape(t))
t=re.sub(r'\n\s*\n+','\n',t)
open(sys.argv[2],'w').write(t)
print('  len',len(t))
PY
fi
