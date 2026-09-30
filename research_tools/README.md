# RescueMesh-AI research toolkit (verified working 2026-09-30)

## IMPORTANT
- The built-in `web_search` tool is BROKEN in this session (HTTP 401 auth error). Do NOT rely on it.
- The `web_fetch` tool WORKS. Use it for known/specific URLs.
- `curl` in bash WORKS for direct URLs and JSON APIs. Bing/Mojeek/DuckDuckGo/SearXNG are captcha-walled — do not waste time.
- Today's access date = **2026-09-30**. Use this as "ngày truy cập".

## 1. Peer-reviewed / topical literature: OpenAlex (BEST tool)
```bash
python3 /home/noble-tran/AIforlife/research_tools/oa.py "your query" 10
# optional 3rd arg = filter, e.g. 'from_publication_date:2015-01-01,type:article'
python3 /home/noble-tran/AIforlife/research_tools/oa.py "LoRa flood monitoring" 8 'from_publication_date:2016-01-01'
```
Returns DOI, title, year, venue, citation count, OA PDF URL, abstract. Handles 429 with backoff.

## 2. Verify a DOI is real (MANDATORY before citing)
```bash
curl -sS -m 25 "https://api.crossref.org/works/10.3390/s18030772" \
 | python3 -c "import json,sys;m=json.load(sys.stdin)['message'];print(m['title'][0]);print(m.get('container-title'));print(m.get('issued'));print(m.get('DOI'))"
```
If Crossref has no such DOI -> the DOI is unverified. Mark it.

## 3. arXiv API (preprints - label as preprint, NOT peer-reviewed)
```bash
curl -sSL -m 25 "https://export.arxiv.org/api/query?search_query=all:%22LoRa%22+AND+all:%22mesh%22&max_results=10" -o /tmp/ax.xml
grep -oP '(?<=<title>).*?(?=</title>)' /tmp/ax.xml
grep -oP '(?<=<id>)http[^<]*' /tmp/ax.xml
```

## 4. Direct fetch (web_fetch tool, or curl)
```bash
curl -sSL -m 20 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36" -o /tmp/p.html "URL"
# then convert to text:
python3 - <<'EOF'
import re,html
t=open('/tmp/p.html',encoding='utf-8',errors='ignore').read()
t=re.sub(r'<(script|style|nav|header|footer).*?</\1>','',t,flags=re.S|re.I)
print(re.sub(r'\s+',' ',html.unescape(re.sub(r'<.*?>',' ',t)))[:4000])
EOF
```

## 5. Reachability notes (tested 2026-09-30, HTTP 200 unless noted)
- vanban.chinhphu.vn OK | thuvienphapluat.vn OK | rfd.gov.vn OK | mic.gov.vn FAILS (000)
- meshtastic.org OK + /docs OK | resources.lora-alliance.org OK | lora-alliance.org = 403
- semtech.com OK | github API = 403 (try raw.githubusercontent.com instead)
- Wikipedia API OK: `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=X&format=json&srlimit=5`

## 6. Output contract for findings
For EVERY claim: `claim | number | source_type | URL or DOI | accessed 2026-09-30 | reliability`.
source_type must be one of: peer-reviewed (DOI) / standard (LoRa Alliance, ETSI, 3GPP) / manufacturer datasheet / Semtech doc / project doc / vendor marketing / preprint (arXiv).
Tier the numbers: FIELD-MEASURED (peer-reviewed) vs THEORETICAL (computed from formula) vs VENDOR-CLAIMED.
If nothing is found: write exactly `KHÔNG TÌM THẤY NGUỒN`. NEVER invent a DOI, title, number or URL.
