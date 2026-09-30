#!/usr/bin/env python3
"""Grounded web search via Gemini + Google Search, with redirect resolution to direct URLs.
Usage: gsearch2.py "query" [model]
"""
import sys, os, json, urllib.request, re

KEY = os.environ.get('GEMINI_API_KEY')
if not KEY:
    try:
        for line in open(os.path.expanduser('~/.dsh/.env')):
            if line.startswith('GEMINI_API_KEY='):
                KEY = line.split('=', 1)[1].strip()
    except Exception:
        pass
if not KEY:
    sys.exit('no GEMINI_API_KEY')

q = sys.argv[1]
model = sys.argv[2] if len(sys.argv) > 2 else 'gemini-2.5-flash'
url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}'
body = {"contents": [{"parts": [{"text": q}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.0}}
req = urllib.request.Request(url, data=json.dumps(body).encode(),
                            headers={'Content-Type': 'application/json'})
import time
d=None
for attempt in range(6):
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            d = json.loads(r.read().decode())
        if 'error' not in d:
            break
        msg = str(d['error'].get('message',''))
        if '429' in msg or 'quota' in msg.lower() or 'rate' in msg.lower():
            time.sleep(20 + attempt*25); continue
        print('ERROR:', msg); sys.exit(1)
    except Exception as e:
        body=''
        try: body=e.read().decode()[:300]
        except Exception: pass
        if '429' in str(e) or '429' in body:
            time.sleep(20 + attempt*25); continue
        print('ERROR:', e, body); sys.exit(1)
if d is None or 'error' in d:
    print('ERROR: rate limited after retries'); sys.exit(1)
cand = (d.get('candidates') or [{}])[0]
for p in (cand.get('content') or {}).get('parts', []):
    if 'text' in p:
        print(p['text'])
gm = cand.get('groundingMetadata') or {}
print('\n== SOURCES ==')
seen = set()
for c in gm.get('groundingChunks') or []:
    w = c.get('web') or {}
    uri, title = w.get('uri'), w.get('title')
    if not uri or uri in seen:
        continue
    seen.add(uri)
    direct = uri
    if 'vertexaisearch' in uri:
        try:
            rq = urllib.request.Request(uri, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(rq, timeout=20) as rr:
                direct = rr.geturl()
        except Exception:
            pass
    print(f'{title} | {direct}')
