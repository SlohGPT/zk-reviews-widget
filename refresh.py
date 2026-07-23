#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obnova recenzií: stiahne NAJNOVŠIE Google + Booking recenzie cez Apify, potom spustí
normalize.py (pridá statické TripAdvisor + prepočíta súhrny) a build.py (prebuildne widget).

POUŽITIE:
    export APIFY_TOKEN=apify_xxxxxxxxxxxxxxxxx
    python3 refresh.py
Výstup: snippet-elementor.html + reviews-widget.json s najnovšími recenziami.
TripAdvisor: bez plateného actora sa nedá scrapovať automaticky — 5 recenzií je statických
v normalize.py; nové TA recenzie tam dopíš ručne (verbatim!), alebo požiadaj Clauda."""
import os, sys, json, time, urllib.request, subprocess

TOKEN = os.environ.get('APIFY_TOKEN')
if not TOKEN:
    sys.exit("CHYBA: nastav APIFY_TOKEN.\n  export APIFY_TOKEN=apify_xxx ; python3 refresh.py")

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://api.apify.com/v2'

def api(method, path, data=None, t=90):
    url = f"{BASE}{path}{'&' if '?' in path else '?'}token={TOKEN}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers={'Content-Type': 'application/json'})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=t) as r:
                return json.load(r)
        except Exception:
            if a == 2: raise
            time.sleep(5)

JOBS = {
    'google': ('compass~crawler-google-places', {
        "searchStringsArray": ["Hotel Zlatý Kľúčik Nitra"], "maxCrawledPlacesPerSearch": 1,
        "language": "sk", "maxReviews": 80, "reviewsSort": "newest", "scrapeReviewsPersonalData": True}),
    'booking': ('voyager~booking-reviews-scraper', {
        "startUrls": [{"url": "https://www.booking.com/hotel/sk/zlaty-klucik.html"}],
        "maxReviewsPerHotel": 100}),
}
runs = {}
for k, (actor, inp) in JOBS.items():
    r = api('POST', f"/acts/{actor}/runs?memory=2048", inp)
    runs[k] = {'id': r['data']['id'], 'ds': r['data']['defaultDatasetId']}
    print("spustené:", k)

done, dl = set(), time.time() + 600
while time.time() < dl and len(done) < len(runs):
    time.sleep(12)
    for k, info in runs.items():
        if k in done: continue
        st = api('GET', f"/actor-runs/{info['id']}")['data']['status']
        if st in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
            done.add(k); print("  ", k, st)

for k, info in runs.items():
    try:
        items = api('GET', f"/datasets/{info['ds']}/items?clean=true&format=json")
    except Exception:
        items = []
    if not isinstance(items, list): items = []
    json.dump(items, open(os.path.join(HERE, f'rev_{k}.json'), 'w'), ensure_ascii=False)
    print(f"uložené rev_{k}.json: {len(items)} položiek")

subprocess.run([sys.executable, os.path.join(HERE, 'normalize.py'), HERE], check=True)
subprocess.run([sys.executable, os.path.join(HERE, 'build.py')], check=True)
print("HOTOVO — snippet-elementor.html + reviews-widget.json sú aktuálne.")
