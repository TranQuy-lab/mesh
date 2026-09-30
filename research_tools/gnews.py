#!/usr/bin/env python3
"""Google News RSS search helper for the RescueMesh legal/context research.

Usage: gnews.py "query" [n]
Prints, for each item: title | source | pubDate | resolved_url

Why this exists: the harness `web_search` tool is broken (HTTP 401), DuckDuckGo
serves bot challenges, and Bing returns near-random results for Vietnamese legal
queries. Google News RSS is a plain feed, so it is reachable with `web_fetch` or
curl and gives real, dated, attributable Vietnamese news items.

The RSS <link> is a news.google.com redirect. We try to resolve it to the
publisher URL with curl -L; if resolution fails we still print the redirect URL
so the caller can fetch it manually.
"""
import sys, re, html, urllib.parse, subprocess

q = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote(q)
       + "&hl=vi&gl=VN&ceid=VN:vi")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36"
raw = subprocess.run(["curl", "-sSL", "-m", "30", "-A", UA, url],
                     capture_output=True, text=True).stdout
items = re.findall(r"<item>(.*?)</item>", raw, re.S)
print(f"# query: {q}  ({len(items)} items)\n")
for it in items[:n]:
    ti = re.search(r"<title>(.*?)</title>", it, re.S)
    lk = re.search(r"<link>(.*?)</link>", it, re.S)
    pd = re.search(r"<pubDate>(.*?)</pubDate>", it, re.S)
    src = re.search(r"<source[^>]*>(.*?)</source>", it, re.S)
    link = html.unescape(lk.group(1)).strip() if lk else ""
    final = link
    if link:
        try:
            r = subprocess.run(["curl", "-sSL", "-m", "20", "-A", UA,
                                "-o", "/dev/null", "-w", "%{url_effective}", link],
                               capture_output=True, text=True)
            cand = r.stdout.strip()
            if cand and "news.google.com" not in cand:
                final = cand
        except Exception:
            pass
    print("-", html.unescape(ti.group(1)) if ti else "")
    print("   src:", html.unescape(src.group(1)) if src else "?",
          "| date:", pd.group(1) if pd else "?")
    print("   url:", final)
    if final != link:
        print("   rss:", link[:120])
