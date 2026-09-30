#!/usr/bin/env python3
"""Search Vietnamese news outlets whose results render server-side.

Usage: psearch.py "query" [site]
  site: vietnamnet | tuoitre | thanhnien | cafef | vtv | dantri | all

Why: the harness `web_search` is broken (HTTP 401) and DuckDuckGo/Bing are
unusable for Vietnamese queries. Google News RSS gives good *discovery* (titles,
source, date) but its article links are JS-only and cannot be resolved, so the
full text must be opened at the publisher. These outlets answer a plain GET with
server-rendered result links, so a short distinctive query here reliably yields
the canonical article URL, which can then be fetched directly.

Tip: use SHORT queries (1-3 words, e.g. "Yagi", "trạm BTS"). Long natural-language
queries often return zero results on these engines.
"""
import sys, re, html, subprocess, urllib.parse

ENDPOINTS = {
    "vietnamnet": "https://vietnamnet.vn/tim-kiem?q={q}",
    "tuoitre":    "https://tuoitre.vn/tim-kiem.htm?keywords={q}",
    "thanhnien":  "https://thanhnien.vn/tim-kiem.htm?keywords={q}",
    "cafef":      "https://cafef.vn/tim-kiem.chn?keywords={q}",
    "vtv":        "https://vtv.vn/tim-kiem.htm?keywords={q}",
    "dantri":     "https://dantri.com.vn/tim-kiem.htm?keywords={q}",
}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36"


def fetch(url):
    return subprocess.run(["curl", "-sSL", "-m", "30", "-A", UA, url],
                          capture_output=True, text=True).stdout


def links(base, page):
    """Return (title, url) for article-looking links, keeping document order."""
    host = urllib.parse.urlparse(base).netloc
    out, seen = [], set()
    for m in re.finditer(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', page,
                         re.S | re.I):
        href, raw = m.group(1), m.group(2)
        # title = text nodes only (drop <img ...> and other tags)
        txt = re.sub(r"<img[^>]*>", " ", raw, flags=re.I)
        txt = re.sub(r"<[^>]+>", " ", txt)
        txt = re.sub(r"\s+", " ", html.unescape(txt)).strip()
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = urllib.parse.urljoin(base, href)
        if host not in href or len(txt) < 22:
            continue
        if not re.search(r"\d{6,}", href):      # article ids are long digit runs
            continue
        if href in seen:
            continue
        seen.add(href)
        out.append((txt, href))
    return out


q = sys.argv[1]
which = sys.argv[2] if len(sys.argv) > 2 else "all"
sites = list(ENDPOINTS) if which == "all" else [which]
for s in sites:
    if s not in ENDPOINTS:
        print("unknown site", s); continue
    url = ENDPOINTS[s].format(q=urllib.parse.quote(q))
    res = links(url, fetch(url))
    print(f"\n===== {s}  ({len(res)} links)  {url}")
    for t, h in res[:14]:
        print(" -", t[:135])
        print("    ", h)
