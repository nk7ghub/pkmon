# Handoff: PKmon (Pokémon card scanner and portfolio)

Moved on 2026-10-13 from `nk7ghub/tamil1-ghub` (private) to its own public repo `nk7ghub/pkmon`, with full commit history. PRs #1–#3 remain in the old repo.

Updated: 2026-10-12

## Files
| File | What it is |
|---|---|
| `index.html` | The whole app (was `PKmon-v1.html` in nk7ghub/tamil1-ghub) in one file (~155 KB): HTML, CSS and JS |
| `pkmon.webmanifest`, `pkmon-icon.svg`, `pkmon-sw.js` | PWA install and offline shell, used on GitHub Pages only |
| `handoff.md` | This note |

Private artifact: https://claude.ai/artifact/FFUoYWj4Yq8E28Dp5Q4o7f
Web version, once GitHub Pages is on: https://nk7ghub.github.io/pkmon/

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

- 2026-10-12 (2): On the phone, both photo buttons still did nothing inside the Claude mobile app; on desktop, both opened the file browser. Cause: the mobile app's artifact web view doesn't open file pickers from the frame, which a page can't override; desktop ignores `capture` by design. Fix:
  - `armPickerWatch`: if no blur, pagehide, visibilitychange, change or cancel event arrives within 1.5 s of a tap, `openPhotoHelp` opens with three options: paste box, "Open with camera" (web version link), and try the picker again.
  - `pasteBox`: an always-visible paste target under the stage in Claude mode, using `imageFilesFrom(clipboardData)`.
  - Drag & drop and Ctrl/⌘+V anywhere on the page (`scanPicked`).
  - Desktop (`TOUCH` false) shows only "Choose photos" plus the drop and paste hint; "Take photo" appears only on touch devices.
  - The "Open with camera" link only works once GitHub Pages is enabled.

- 2026-10-12 (3): Cards photographed in Chrome were "not recognised". Causes:
  - The user opened a downloaded copy (`content://`), which ran offline.
  - Pages serves the default branch `ccr-fd6ba824-w6y900`, which only had v1.
  - The photo crop assumed the card fills the frame.
  - OCR read a 630 px downscale.
  - The number regex missed `TG20/TG30`.
  - A stray "null" button label.

  Fix:
  - `locateCard`: edge-continuity profiles plus a 63:88 pair search.
  - OCR from a full-resolution crop with ~1.1k–1.8k px strips; multi-pass Tesseract (PSM 6/11, contrast/plain); stops at the first parsed number.
  - `parseCardNumber` handles TG/GG/SV plus OCR noise; `nameInText` is a 4-gram fuzzy name filter.
  - TCGdex backup (`dexFind`, `mapDex`, `fetchCardsAny`).
  - Probe waits 20 s and checks both APIs; OCR timeouts (60 s load, 30 s per pass).
  - On a miss, the scanner search box is filled with the OCR guess.
  - Verified with real Tesseract on the user's Rayquaza photo: read `TG20/30` and matched swsh12tg-TG20 via pokemontcg.io and via TCGdex.

- 2026-10-13 Phase 1 (recognition): OCR alone was too unreliable on real cards ("ikachuVI", "#7/17"). Added:
  - `CardIndex`: the full TCGdex card list (id, number, name, image) plus set sizes, cached 7 days in Cache Storage. `rank()` scores every card using the exact number, set size, trigram name containment, an evidence bonus and a V/VMAX/VSTAR suffix rule. `numberCandidates()` turns noisy pairs like "1157/1725" into 157/172, kept only if a real set has that size.
  - `detailsFor()` fetches the top 12 (pokemontcg.io, else TCGdex). HP (digits found anywhere in the OCR text) gives +12; an attack or ability name in the text gives +20.
  - "Sure" means score ≥ 90 with a lead of 12+, or ≥ 65 with a lead of 25+. Otherwise a "Which card is this?" grid (`.pickgrid`) shows the photo next to the top 8; one tap adds the card. Stack mode only auto-adds sure matches.
  - `splitCards()`: wide or tall photos are split into one crop per card.
  - Fixed: live grade not rounded; background `render()` rebuilt the scanner mid-camera or mid-scan (guard plus restoring `Scan.lastStill`); auto-capture now needs conf > .5 and sharpness.
  - Search box uses `CardIndex.search` (typo-tolerant).
  - Tested with real Tesseract on the user's photos against a 1,201-card decoy index with pokemontcg.io down: Pikachu V 157/172 sure (129), Rayquaza VMAX TG20 sure (120), Octillery TG03 sure (76); Acerola TG24 and Gloria put the right card first in the grid.
  - Not done: full perspective (keystone) correction. The edge finder plus 63:88 shape rule covered the test photos.

- 2026-10-13 (stack + install):
  - **Multi-card photos:** `splitCards()` now finds the background gaps between cards from a per-column texture profile, cuts any part wider than ~1.5 cards at its plainest column, and falls back to equal strips. Verified on the user's 3-card photo, a 2-card crop, uneven gaps and a 4-card mix.
  - **Batch review:** `identify(..., batch)` returns its result; `fromFiles` collects them into a `state: "batch"` view with one row per card and a pick grid per unsure card. Stack mode now also adds unsure cards as the best guess with `item.check = true` (a "Check" chip); picking from the grid replaces it, and saving the detail page clears the flag.
  - **Live-site bugs:** `[hidden]` rule added to our own CSS (the artifact frame supplied it, GitHub Pages didn't, so the "pick photos" overlay never hid). `index.html` now starts with doctype, `meta charset` and a `viewport` meta; without viewport the Pages site rendered at desktop width on phones. The artifact is published from a copy without those three lines.
  - **Install:** PNG icons (192, 512, maskable 512, apple-touch 180), a full manifest (`id`, `scope`, `display_override`, `shortcuts` to `#scan`/`#port`), SW shell v3. `Install` object: `beforeinstallprompt` one-tap on Chrome/Edge/Android; Safari Share → Add to Home Screen steps on iPhone/iPad; inside Claude it opens `PUBLIC_URL#install`. The header button hides when running standalone. Chrome's own installability check reports no errors.

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
