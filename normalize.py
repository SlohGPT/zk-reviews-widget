#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalizácia surových dát (rev_google.json + rev_booking.json) -> reviews.json + meta.json
Pravidlo: recenzia sa berie, ak má TEXT (>=25 znakov) ALEBO FOTKY (photo-only = štýl Trustindex
"Tento používateľ zanechal iba hodnotenie."). TripAdvisor = statický zoznam (verbatim z live
stránky cez WebFetch 2026-07-23; scraper aktori nedostupné na FREE pláne)."""
import json, re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = sys.argv[1] if len(sys.argv) > 1 else '/tmp'

def gv(d, *ks):
    for x in ks:
        v = d.get(x)
        if v not in (None, '', [], {}): return v
    return None

google = json.load(open(os.path.join(RAW, 'rev_google.json')))
booking = json.load(open(os.path.join(RAW, 'rev_booking.json')))
place = google[0] if google else {}

rows = []
for r in place.get('reviews', []):
    txt = (gv(r, 'text', 'textTranslated') or '').strip()
    imgs = (r.get('reviewImageUrls') or [])[:4]
    if not txt and not imgs: continue
    rows.append({'source': 'google', 'name': gv(r, 'name'), 'location': None,
                 'avatar': gv(r, 'reviewerPhotoUrl'), 'rating': r.get('stars') or 5,
                 'time': gv(r, 'publishedAtDate'), 'text': txt, 'images': imgs})
for r in booking:
    txt = (r.get('likedText') or '').strip()
    if not txt: continue
    r10 = r.get('rating') or r.get('hotelRating') or 10
    rows.append({'source': 'booking', 'name': gv(r, 'userName') or 'Hosť', 'location': gv(r, 'userLocation'),
                 'avatar': None, 'rating': round(r10 / 2.0, 2), 'rating10': r10,
                 'time': gv(r, 'reviewDate'), 'text': txt, 'images': []})

# TripAdvisor — verbatim texty z live TA stránky (page 1), 2026-07-23
TA = [
 {'name': 'Fee_J_80', 'time': '2025-09-01T12:00:00Z', 'rating': 5, 'title': 'Simply the best!',
  'text': "This was my second stay at the hotel while travelling with work. I absolutely love everything about this hotel. The rooms, the food, the staff are exceptional. I would never stay anywhere else. As I travel alone I didn't feel like going for dinner on my own so ordered room service, the food was superb! Next time I will have to give the spa a whirl. THANKYOU for such a wonderful stay"},
 {'name': 'TheFifthBeatle', 'time': '2025-05-01T12:00:00Z', 'rating': 5, 'title': 'Fancy stay and relax',
  'text': "We did not know what to expect but we were positively surprised. Very polite and friendly stuff and spacious rooms. So comfortable beds! The breakfast and dinners were delicious and waiters very helpful, they described all dishes with details. Moreover, food was served quickly and was so tasty and fresh. Also, the breakfast menu was very good, we loved the pastries ❤️ The stay was rich with extras like spa, which was amazing. We are so relaxed now!"},
 {'name': 'Bruce', 'time': '2023-09-01T12:00:00Z', 'rating': 5, 'title': 'Great hotel in Nitra',
  'text': "Stayed here for three nights at the end of August, celebrating in-laws birthdays and wedding anniversary. Lovely hotel, clean in all common areas and spacious well-appointed rooms, with excellent food for lunch and dinner in the hotel restaurant, served by attentive staff. The wellness centre is fantastic. You can book use of the wellness centre in 2-hr blocks, so plenty of time to relax and enjoy all the different facilities."},
 {'name': 'Sylvia V', 'time': '2022-11-01T12:00:00Z', 'rating': 5, 'title': 'Autumn relaxation',
  'text': "A wonderful hotel in a beautiful environment, with very nice staff, excellent massages, and a very pleasant environment. We cannot imagine a better place for autumn relaxation. We will definitely be happy to come back."},
 {'name': 'Alexandra', 'time': '2022-09-01T12:00:00Z', 'rating': 5, 'title': 'Amazing hotel with great services',
  'text': "Hotel is located on a hill where the view is just brilliant. Staff was very welcoming and the room was spacious and clean. Same was the wellness center - nice and quiet, just for us. Definitely worth booking"},
]
TA_SK = {'Fee_J_80': 'Toto bol môj druhý pobyt v hoteli počas pracovných ciest. Na tomto hoteli absolútne milujem všetko. Izby, jedlo aj personál sú výnimočné. Nikdy by som sa neubytovala nikde inde. Keďže cestujem sama, nechcelo sa mi ísť na večeru samej, tak som si objednala izbovú službu – jedlo bolo vynikajúce! Nabudúce musím vyskúšať aj spa. ĎAKUJEM za nádherný pobyt.', 'TheFifthBeatle': 'Nevedeli sme, čo očakávať, ale boli sme pozitívne prekvapení. Veľmi zdvorilý a priateľský personál a priestranné izby. Aké pohodlné postele! Raňajky a večere boli vynikajúce a čašníci veľmi ochotní, všetky jedlá nám podrobne opísali. Jedlo bolo navyše servírované rýchlo, chutné a čerstvé. Raňajkové menu bolo veľmi dobré, zamilovali sme si pečivo ❤️ Pobyt bol bohatý na extra služby ako spa, ktoré bolo úžasné. Sme teraz takí oddýchnutí!', 'Bruce': 'Skvelý hotel v Nitre s rovnako skvelým a ochotným personálom. Koncom augusta sme tu strávili tri noci, oslavovali sme narodeniny a výročie svadby svokrovcov. Krásny hotel, čistý vo všetkých spoločných priestoroch, priestranné a dobre vybavené izby, s výborným jedlom na obed aj večeru v hotelovej reštaurácii a pozorným personálom. Wellness centrum je fantastické. Vstup sa dá rezervovať v 2-hodinových blokoch, takže je dosť času na oddych a všetky procedúry.', 'Sylvia V': 'Nádherný hotel v krásnom prostredí, s veľmi milým personálom, vynikajúcimi masážami a veľmi príjemnou atmosférou. Lepšie miesto na jesenný relax si nevieme predstaviť. Určite sa radi vrátime.', 'Alexandra': 'Hotel sa nachádza na kopci, odkiaľ je jednoducho úžasný výhľad. Personál bol veľmi milý a izba priestranná a čistá. Rovnako aj wellness centrum – pekné a tiché, len pre nás. Určite stojí za rezerváciu.'}
for r in TA:
    rows.append({'source': 'tripadvisor', 'name': r['name'], 'location': None, 'avatar': None,
                 'rating': r['rating'], 'time': r['time'], 'text': r['text'],
                 'text_sk': TA_SK.get(r['name']), 'images': []})

seen, out = set(), []
for x in rows:
    if (x['rating'] or 0) < 4: continue
    t = re.sub(r'\s+', ' ', x['text']).strip()
    if t and len(t) < 25 and not x['images']: continue
    x['text'] = t
    key = (x['source'], (x['name'] or '').lower(), t[:40].lower())
    if key in seen: continue
    seen.add(key); out.append(x)
out.sort(key=lambda x: x['time'] or '', reverse=True)

meta = {
 'google': {'rating': place.get('totalScore') or 4.7, 'count': place.get('reviewsCount') or 979,
            'write': 'https://search.google.com/local/writereview?placeid=' + (place.get('placeId') or 'ChIJn0vM59U-a0cRGGfFsJDDbeY')},
 'booking': {'rating': (booking[0].get('hotelRating') if booking else 9.5) or 9.5,
             'count': (booking[0].get('hotelReviews') if booking else 858) or 858,
             'write': 'https://www.booking.com/hotel/sk/zlaty-klucik.html'},
 'tripadvisor': {'rating': 4.5, 'count': 100,
                 'write': 'https://www.tripadvisor.com/UserReviewEdit-g274933-d583417'},
}
tc = sum(m['count'] for m in meta.values())
tw = (meta['google']['rating'] * meta['google']['count'] + (meta['booking']['rating'] / 2.0) * meta['booking']['count']
      + meta['tripadvisor']['rating'] * meta['tripadvisor']['count']) / tc
meta['total'] = {'rating': round(tw, 1), 'count': tc}

json.dump(out, open(os.path.join(HERE, 'reviews.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(meta, open(os.path.join(HERE, 'meta.json'), 'w'), ensure_ascii=False, indent=1)
print("reviews:", len(out), {s: sum(x['source'] == s for x in out) for s in ('google', 'booking', 'tripadvisor')},
      "| photo-only:", sum(1 for x in out if not x['text']),
      "| total:", meta['total'])
