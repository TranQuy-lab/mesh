#!/usr/bin/env python3
"""OpenAlex topical search. Usage: oa.py "query" [n]
Prints: DOI | title | year | venue | cited_by | abstract(400 chars) | oa_url
Retries on 429 with backoff."""
import sys, json, time, urllib.parse, urllib.request

def get(url, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'RescueMeshResearch/1.0 (mailto:researcher@example.org)',
                'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if i == tries - 1:
                return {'error': str(e)}
            time.sleep(8 + i * 7)
    return {}

def inv2text(inv):
    if not inv: return ''
    pos = {}
    for w, idxs in inv.items():
        for i in idxs: pos[i] = w
    return ' '.join(pos[k] for k in sorted(pos))

def main():
    q = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    filt = sys.argv[3] if len(sys.argv) > 3 else ''
    url = ('https://api.openalex.org/works?search=' + urllib.parse.quote(q) +
           f'&per-page={n}&mailto=researcher@example.org')
    if filt: url += '&filter=' + filt
    d = get(url)
    if 'error' in d:
        print('ERROR:', d['error']); return
    print(f"# query={q}  total={d.get('meta',{}).get('count')}")
    for w in d.get('results', []):
        src = ((w.get('primary_location') or {}).get('source') or {})
        ab = inv2text(w.get('abstract_inverted_index'))[:400].replace('\n', ' ')
        print('---')
        print('DOI :', w.get('doi'))
        print('T   :', w.get('title'))
        print('Y   :', w.get('publication_year'), '|', src.get('display_name'), '| type=', w.get('type'))
        print('CIT :', w.get('cited_by_count'), '| OA:', (w.get('open_access') or {}).get('oa_url'))
        if ab: print('ABS :', ab)

main()
