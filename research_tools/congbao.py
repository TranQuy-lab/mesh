#!/usr/bin/env python3
"""Official Vietnamese Cong Bao (Official Gazette) search helper.

Usage:
  congbao.py search "08/2021/TT-BTTTT" [n]
  congbao.py doc    "08/2021/TT-BTTTT"      # exact record + PDF/DOC download URLs

Why: congbao.chinhphu.vn renders its search client-side, so a plain GET returns an
empty shell. Its real backend is a public JSON API, discovered in the site's
minified JS (static.mediacdn.vn/CongBao/min/main-*.min.js):

  POST https://api-searchcongbao.chinhphu.vn/search/van-ban
  body: {"filters":{},"page":1,"page_size":N,"query":"..."}

Every record carries `danh_sach_tep_van_ban[].duong_dan`, i.e. the canonical
congbaocdn.chinhphu.vn PDF of the document as published in the Official Gazette.
That PDF is the primary source: prefer it over any secondary legal site.
"""
import sys, json, urllib.request

API = "https://api-searchcongbao.chinhphu.vn/search/van-ban"


def query(q, n=10):
    body = json.dumps({"filters": {}, "page": 1, "page_size": n,
                       "query": q}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": "application/json",
        "Origin": "https://congbao.chinhphu.vn",
        "Referer": "https://congbao.chinhphu.vn/",
        "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.loads(r.read().decode())
    items = d.get("data") or []
    if isinstance(items, dict):
        items = items.get("data") or []
    return items


def show(it, full=False):
    print("-", it.get("so_ky_hieu"), "|", (it.get("ngay_ban_hanh") or "")[:10],
          "|", it.get("loai_van_ban"), "|", (it.get("ten_co_quan") or [""])[0])
    ty = (it.get("trich_yeu") or "").strip()
    if ty:
        print("   trích yếu:", ty[:220])
    hl = it.get("ngay_co_hieu_luc")
    if hl:
        print("   hiệu lực:", hl[:10])
    if full:
        print("   id_van_ban:", it.get("id_van_ban"))
        for f in it.get("danh_sach_tep_van_ban") or []:
            print("   file:", f.get("file_extension"), f.get("duong_dan"))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "search"
    if mode == "doc":
        q = sys.argv[2]
        for it in query(q, 10):
            if str(it.get("so_ky_hieu", "")).strip().lower() == q.strip().lower():
                show(it, full=True)
                break
        else:
            print("no exact match; closest:")
            for it in query(q, 5):
                show(it)
    else:
        q = sys.argv[2]
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        print(f"# congbao search: {q}  ({len(query(q,n))} of first {n} shown)\n")
        for it in query(q, n):
            show(it)


if __name__ == "__main__":
    main()
