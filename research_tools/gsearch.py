#!/usr/bin/env python3
"""Grounded web search via Gemini + Google Search.
Usage: gsearch.py "query"  [model]
Prints answer text then '== SOURCES ==' with the grounding URLs (title | uri).
"""
import sys, os, json, urllib.request

KEY = os.environ.get('GEMINI_API_KEY')
if not KEY:
    # read from ~/.dsh/.env
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
body = {
    "contents": [{"parts": [{"text": q}]}],
    "tools": [{"google_search": {}}],
    "generationConfig": {"temperature": 0.0},
}
req = urllib.request.Request(url, data=json.dumps(body).encode(),
                            headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read().decode())
except Exception as e:
    print('ERROR:', e)
    try:
        print(e.read().decode()[:800])
    except Exception:
        pass
    sys.exit(1)

if 'error' in d:
    print('ERROR:', d['error'].get('message')); sys.exit(1)
cand = (d.get('candidates') or [{}])[0]
for p in (cand.get('content') or {}).get('parts', []):
    if 'text' in p:
        print(p['text'])
gm = cand.get('groundingMetadata') or {}
chunks = gm.get('groundingChunks') or []
print('\n== SOURCES ==')
seen = set()
for c in chunks:
    w = c.get('web') or {}
    uri, title = w.get('uri'), w.get('title')
    if uri and uri not in seen:
        seen.add(uri)
        print(f'{title} | {uri}')
