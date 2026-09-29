#!/usr/bin/env bash
# Scholarly search helper. Usage:
#   schol.sh ddg "query" [n]      -> DuckDuckGo results (title + url)
#   schol.sh cr  "query"          -> Crossref bibliographic matches
#   schol.sh oa  "query"          -> OpenAlex search (retries on 429)
#   schol.sh doi "10.x/y"         -> Crossref metadata for a DOI
#   schol.sh oadoi "10.x/y"       -> OpenAlex metadata for a DOI
#   schol.sh ax  'all:term'       -> arXiv API (properly encoded)
#   schol.sh fetch URL            -> raw page text (first 40k chars, tags stripped)
set -uo pipefail
UA="ResearchBot/1.0 (mailto:research@example.org)"

case "${1:-}" in
ddg)
  Q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote_plus(sys.argv[1]))" "$2")
  N=${3:-8}
  curl -sL -A "Mozilla/5.0 (X11; Linux x86_64)" --max-time 25 "https://html.duckduckgo.com/html/?q=$Q" -o /tmp/_ddg.html
  python3 - "$N" <<'EOF'
import re,html,urllib.parse,sys
n=int(sys.argv[1])
s=open('/tmp/_ddg.html',encoding='utf8',errors='ignore').read()
for u,t in re.findall(r'result__a" href="([^"]+)"[^>]*>(.*?)</a>',s)[:n]:
    m=re.search(r'uddg=([^&]+)',u)
    url=urllib.parse.unquote(m.group(1)) if m else u
    print(html.unescape(re.sub('<[^>]+>','',t))[:110],'\n   ',url)
EOF
  ;;
cr)
  Q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote_plus(sys.argv[1]))" "$2")
  curl -s --max-time 30 -H "User-Agent: $UA" "https://api.crossref.org/works?query.bibliographic=$Q&rows=6" \
   | jq -r '.message.items[]? | "\(.issued."date-parts"[0][0]) | \(.title[0]) | \(.DOI) | \(.["container-title"][0] // "n/a") | cites:\(.["is-referenced-by-count"])"'
  ;;
oa)
  Q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote_plus(sys.argv[1]))" "$2")
  for i in 1 2 3 4 5; do
    R=$(curl -s --max-time 30 -H "User-Agent: $UA" "https://api.openalex.org/works?search=$Q&per-page=8&mailto=research@example.org")
    if ! echo "$R" | grep -q 'Rate limit'; then break; fi; sleep 20
  done
  echo "$R" | jq -r '.results[]? | "\(.publication_year) | \(.title) | \(.doi) | \(.primary_location.source.display_name // "n/a") | cites:\(.cited_by_count)"'
  ;;
doi)
  curl -s --max-time 30 -H "User-Agent: $UA" "https://api.crossref.org/works/$2" \
   | jq -r '.message | "\(.issued."date-parts"[0][0]) | \(.title[0]) | \(.DOI) | \(.["container-title"][0] // "n/a") | authors:\([.author[]?|(.family//"")]|join(", ")) | cites:\(.["is-referenced-by-count"])"'
  ;;
oadoi)
  curl -s --max-time 30 -H "User-Agent: $UA" "https://api.openalex.org/works/doi:$2?mailto=research@example.org" \
   | jq -r '"\(.publication_year) | \(.title) | \(.doi) | \(.primary_location.source.display_name // "n/a") | cites:\(.cited_by_count) | oa:\(.open_access.is_oa) | \(.best_oa_location.pdf_url // "no-pdf")"'
  ;;
ax)
  curl -sL -A "curl/8.5.0" -G --max-time 30 "https://export.arxiv.org/api/query" \
    --data-urlencode "search_query=$2" --data-urlencode "start=0" --data-urlencode "max_results=8" --data-urlencode "sortBy=relevance" \
  | python3 -c "
import sys,xml.etree.ElementTree as ET
ns={'a':'http://www.w3.org/2005/Atom'}
try: t=ET.fromstring(sys.stdin.read())
except Exception as e: print('PARSE-ERR',e); raise SystemExit
for e in t.findall('a:entry',ns):
    print(e.find('a:published',ns).text[:4],'|',e.find('a:title',ns).text.strip().replace(chr(10),' ')[:110],'|',e.find('a:id',ns).text)
"
  ;;
fetch)
  curl -sL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36" --max-time 35 "$2" \
  | python3 -c "
import sys,re,html
s=sys.stdin.read()
s=re.sub(r'(?is)<(script|style|nav|footer|svg)[^>]*>.*?</\1>',' ',s)
s=html.unescape(re.sub('<[^>]+>',' ',s))
s=re.sub(r'[ \t\xa0]+',' ',s); s=re.sub(r'\n\s*\n+','\n',s)
print(s[:40000])
"
  ;;
*) echo "usage: schol.sh {ddg|cr|oa|doi|oadoi|ax|fetch} arg"; exit 1;;
esac
