# zk-reviews-widget

Self-hosted reviews widget for **Hotel Zlatý Kľúčik** (zlatyklucik.sk) — a free, owned replica of
the Trustindex architecture: tiny permanent embed on the site, widget code + data served from this
repo via jsDelivr CDN, and a weekly GitHub Actions cron that re-scrapes reviews and publishes them.

## How it works (Trustindex model, $0)
```
WordPress (never changes)                 this repo (updates itself)
┌───────────────────────────┐   fetch    ┌─────────────────────────────┐
│ <div class="zkr-wrap">    │ ─────────▶ │ widget.js   (code, CDN)     │
│ <script src=…widget.js>   │            │ reviews-widget.json (data)  │
└───────────────────────────┘            └──────────▲──────────────────┘
                                                    │ commits fresh JSON
                                         GitHub Actions cron (Mon 04:00)
                                         └ Apify scrape: Google + Booking
```

## Embed (paste ONCE into an Elementor HTML widget)
```html
<div class="zkr-wrap"></div>
<script src="https://cdn.jsdelivr.net/gh/SlohGPT/zk-reviews-widget@main/widget.js" defer></script>
```

## Files
| file | role |
|---|---|
| `widget.js` | the whole widget (CSS+JS+fallback data) — served via jsDelivr |
| `reviews-widget.json` | fresh data (meta totals, tabs, reviews) — fetched by widget.js |
| `embed-wp.html` | the 2-line embed for WordPress |
| `refresh.py` | scrapes Google (compass) + Booking (voyager) via Apify |
| `normalize.py` | raw → reviews.json + meta.json (adds static TripAdvisor + SK translations) |
| `build.py` | builds the inline snippet (snippet-elementor.html) from data |
| `build_remote.py` | snippet → widget.js + embed-wp.html |
| `.github/workflows/refresh.yml` | the Monday cron |

## Notes
- Relative dates ("pred 2 dňami") are computed client-side at every page load — always current.
- Widget UI is localized SK/EN/DE (auto-detected from GTranslate /en/ /de/ paths).
- TripAdvisor has no free scraper → 5 verbatim reviews are static in `normalize.py`; add new ones by hand.
- jsDelivr caches `@main` ~12 h → new reviews appear on the site within ~half a day after the cron run.
- Requires repo secret **APIFY_TOKEN** (Apify free plan covers weekly runs).
