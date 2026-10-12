# Handoff: PKmon-v1 (Pokémon card scanner and portfolio)

Updated: 2026-10-12

## Files
| File | What it is |
|---|---|
| `PKmon-v1.html` | The whole app in one file (~155 KB): HTML, CSS and JS |
| `pkmon.webmanifest`, `pkmon-icon.svg`, `pkmon-sw.js` | PWA install and offline shell, used on GitHub Pages only |
| `handoff.md` | This note |

Private artifact: https://claude.ai/artifact/FFUoYWj4Yq8E28Dp5Q4o7f
Web version, once GitHub Pages is on: https://nk7ghub.github.io/tamil1-ghub/PKmon-v1.html

## Two modes, one file
The app checks for `window.claude.use` at startup.

| | Web (GitHub Pages) | Claude artifact |
|---|---|---|
| Card ID | Tesseract.js OCR reads the name and `123/165`, then looks the card up on pokemontcg.io | Claude vision through `sample.json` with images |
| Camera | Live `getUserMedia` feed, AR grid, auto-capture when the card is steady | Photo picker (`capture=environment`, multiple) |
| Prices | Live TCGplayer and Cardmarket via pokemontcg.io, cached 24h, refreshed every 30 min while open | Last saved snapshot, or a Claude estimate (labelled) |
| Storage | localStorage | `db` at `data/users/<uid>/vault` (meta doc), plus `/items/*` and `/alerts/*` subcollections; localStorage mirror |
| Downloads | Blob link | `downloads.save` |
| Exchange rates | open.er-api.com, then Frankfurter, then built-in table | Built-in table |

To move a vault between modes: Export → Full backup (JSON), then Settings → Restore backup.

## Key code areas (search for these names)
- `Grader.analyze`: centering from gradient profiles (outer card edge, then inner frame); corners and edges from whitening and straightness; surface from fine-line and glare checks. Overall = average of the four, capped at the lowest + 1.5, rounded to 0.5.
- `Foil`: holo vs reverse holo from frame-to-frame sparkle changes inside vs outside the art box.
- `Scan.capture / identify / fromFiles`: stack scanning and duplicate guard (6 s).
- `gradedUSD`: PSA/BGS/CGC **model estimates** (multiplier by price tier, plus a grading-cost floor). Not market data.
- `trendSeries`: chart = your daily snapshots plus points rebuilt from Cardmarket's avg30/avg7/avg1.
- `exportPDF`: jsPDF 2.5.1 + autotable 3.8.2 (cdnjs), landscape A4 with thumbnails, sub-scores, sealed, sets and alerts.
- `packBinder / renderBinder`: share link = deflate-raw + base64url of the card IDs in `#b=`. Opens read-only on the web version.

## Fix log
- 2026-10-12: "Take or choose photos" did nothing. Cause: a `display:none` file input opened by script `.click()`, which iOS and the Claude frame ignore. `capture` also blocked the gallery, and undecodable photos were skipped silently. Fix: native `<label for>` buttons (`pickBtn`) for two inputs, `#camIn` (camera) and `#fileIn` (gallery, multiple), kept visually hidden but not `display:none`. `decodeImage` falls back to `<img>`. A live "Scanning photo X of Y · %" bar (`setPhotoProgress`) shows progress, errors show as toasts, and Claude always gets a JPEG crop. The 6-second duplicate guard now applies to the live camera only.

## Tested (headless Chromium, recorded API responses)
- No JS errors; no sideways scroll at 400 px or 1280 px; light and dark themes.
- Search → add → portfolio KPIs, INR conversion, detail page, raw/graded table, alert, sealed add, master-set %, CSV (29 columns), PDF (26 KB), text list, trade verdict, binder link round-trip.
- Grader on a synthetic card: measured L/R 40/60 against a true 38/62, centering score 9.
- Claude-mode fallback when every capability returns null.

## Not tested, or known limits
- **Live APIs not tested from the build container** (its network proxy blocks pokemontcg.io and the rate APIs). The code follows the documented v2 schema.
- Real camera, OCR accuracy and Claude vision were not run here. They need a phone and the live artifact.
- eBay has no free sold-price API, so the app opens the sold-listings search. PSA/BGS/CGC values are estimates, with links to PSA APR and 130point.
- Price alerts fire only while the app is open. Closed-app push would need a server.
- pokemontcg.io allows about 1,000 calls a day without a key. Add a free key in Settings.

## Next steps
1. Repo Settings → Pages → deploy from this branch (or merge to main), root folder.
2. Open the Pages URL on a phone and scan 3–5 real cards; tune `Grader` thresholds if centering is off.
3. Optional: add a price-history backend, then real eBay sold data through a server proxy.
