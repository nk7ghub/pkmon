# Handoff: PKmon Card Vault

Pokémon TCG card scanner, condition pre-grader, multi-market pricing and portfolio tracker, built as a single-file PWA.

Updated: 2026-10-13

| Where | Link |
|---|---|
| Live app (GitHub Pages, `main`, root) | https://nk7ghub.github.io/pkmon/ |
| Repo (public) | https://github.com/nk7ghub/pkmon |
| Claude artifact (private, owner only) | https://claude.ai/artifact/FFUoYWj4Yq8E28Dp5Q4o7f |
| Origin | Started in `nk7ghub/tamil1-ghub` as `PKmon-v1.html` (PRs #1–#4 there), moved here on 2026-10-13 with full history |

Always open the **https** link. A downloaded copy (`file://` or `content://`) has no live prices, camera or install; the app warns about this.

## Files
| File | What it is |
|---|---|
| `index.html` | The whole app (~220 KB): HTML, CSS and JS. Starts with doctype, charset and viewport for the web version. |
| `pkmon.webmanifest` | PWA manifest: id, scope, icons, shortcuts `#scan` / `#port` |
| `pkmon-sw.js` | Service worker: offline app shell (`pkmon-shell-v3`), network-first, never caches API calls |
| `pkmon-192.png`, `pkmon-512.png`, `pkmon-maskable-512.png`, `apple-touch-icon.png`, `pkmon-icon.svg` | App icons |
| `README.md`, `handoff.md` | Docs |

**Publishing the artifact:** strip the first 3 lines of `index.html` (doctype, charset, viewport; the artifact frame supplies its own), e.g. `tail -n +4 index.html > artifact.html`, then publish to the artifact URL above. Capabilities declared: `sample` (images), `db`, `downloads`, `user`.

## Two modes, one file
At startup the app checks for `window.claude.use`.

| | Web (GitHub Pages) | Claude artifact |
|---|---|---|
| Card ID | OCR (Tesseract.js 5.1.1) → local card index → picture check | Claude vision (`sample.json` with images) |
| Camera | Live `getUserMedia`, AR grid, auto-capture when steady | Photo picker; paste/drop fallback (the mobile app blocks pickers) |
| Prices | pokemontcg.io + TCGdex, cached 24 h, refreshed every 30 min | Last saved snapshot or Claude estimate (labelled) |
| Storage | localStorage | `db` (`data/users/<uid>/vault`, `/items/*`, `/alerts/*`) plus a localStorage mirror |
| Install | Install button (Chrome/Edge/Android prompt; iPhone steps) | Button opens the web version (frames can't install) |
| Back button | Browser history steps (phone Back works) | On-screen Back only |

## How a scan works (web)
1. **Photo → cards.** `splitCards()` finds the background gaps between cards (per-column texture profile) and cuts any part wider than ~1.5 cards at its plainest column. Limits: `MAX_PER_PHOTO = 6` (one row; 3–4 reads best), `MAX_PHOTOS = 30` per batch; the live camera is unlimited, one card at a time.
2. **Find the card.** `locateCard()` takes edge-continuity profiles plus a 63:88 pair search. The grader gets the exact crop; OCR gets a slightly larger full-resolution crop.
3. **Grade.** `Grader.analyze`: centering from border widths (PSA 55/45 = 10); corners and edges from whitening and straightness; surface from fine lines and glare. `Foil` tracks shimmer between frames.
4. **Read text.** `Scan.ocrRead`: up to 4 number passes (stop at the first parse), 1–2 name passes, 1 full-card pass (850 px). `parseCardNumber` / `numberCandidates` handle `057/195`, `TG20/TG30`, `GG35/GG70`, `SV107/SV122` and noise like `1157/1725`. Name candidates skip "Evolves from X".
5. **Card list.** `CardIndex`: the full TCGdex card list (id, number, name, image) plus set sizes, streamed with % progress and cached 7 days in Cache Storage. It's downloaded once per session; after a failure it isn't retried for 2 min. If the download stalls for 7 s, that scan continues without it (`CardIndex.stalled`) and later cards don't wait.
6. **Rank.** `CardIndex.rank`: exact number +45, set size +25, fuzzy number pair +65, trigram name containment up to +40 plus an evidence bonus, V/VMAX/VSTAR suffix ±. A strong read takes the top 12; a weak read (< 60) takes a pool of 24, plus same-name prints (max 30).
7. **Picture check.** `Visual`: 8×11 lighting-normalised colour grid plus a 16×16 gradient hash vs each candidate's TCGdex image (`/low.webp`). Up to +45, relative within the pool; 4 s per image, 8 s overall.
8. **Details.** `detailsFor`: asks TCGdex and pokemontcg.io at the same time, waits at most ~1.5 s for pokemontcg.io after TCGdex answers (8 s budget). A slow pokemontcg.io is remembered (`ENV.ptcgSlow`) and skipped for the session. HP digits in the text +12; an attack or ability name in the text +20.
9. **Decide.** "Sure" = score ≥ 90 with a lead ≥ 12, or ≥ 65 with a lead ≥ 25 (never from a weak-read pool). Otherwise the result shows a pick grid. Stack mode adds unsure cards as the best guess with `item.check = true`.
10. **Without the card list:** TCGdex search (number, then the top 3 name prefixes, in parallel, 12 s budget) → picture-ordered → always marked Check.
11. **Timing.** Every result carries `timing` ("9.4 s · read 7.2 s · pictures 0.7 s · lookup 1.5 s"), shown under each batch row and logged to the console. Settings shows the card list status, with a "Download card list now" button.

## Fixing wrong cards
- **Where to start:** the "Check ›" chip in any list, the Portfolio "N cards to check · Review" bar (`openReview`), the detail page bar ("It's correct" / "Change card"), or "Change" on batch rows.
- **`openReplace(it)`:** same-name prints → V/VMAX/ex versions → similar names (max 30), ordered by picture match to `it.thumb`, plus search.
- **`replaceItem(old, card)`:** keeps id, qty, paid, grade, notes and alerts, and clears `check`.

## Navigation
`Nav` gives each screen change and first sheet a `history.pushState`. Phone Back closes the sheet, then steps back through screens. A root entry means Back at the first screen shows "Press back again to close PKmon". `#backBtn` sits in the header and a Back button tops every sheet; the header compacts below 460 px. Inside Claude, history is untouched.

## Install (PWA)
The `Install` object: `beforeinstallprompt` on Chrome/Edge/Android; Safari Share → Add to Home Screen steps on iPhone/iPad; the Claude artifact links to `PUBLIC_URL#install`; downloaded copies get a sheet pointing to the live site. The button is hidden when running standalone. Chrome's DevTools installability check reports no errors.

## Other features (unchanged)
- Portfolio KPIs and a 30D/1Y chart (daily snapshots + Cardmarket avg30/7/1); sealed products; master-set progress; 33 currencies.
- Raw vs PSA/BGS/CGC model estimates; price alerts; trade analyzer.
- CSV/text/PDF (jsPDF 2.5.1 + autotable 3.8.2)/JSON export; binder share links (`#b=` deflate + base64url).

## Change log
| Date | Change |
|---|---|
| 2026-10-12 | v1 built (artifact + Pages). Photo picker fixes: native `<label for>` inputs, paste/drop, blocked-picker detector. |
| 2026-10-12 | Recognition v1: `locateCard`, full-res multi-pass OCR, TG/GG/SV numbers, TCGdex backup. |
| 2026-10-13 | Phase 1: `CardIndex` ranking, pick grid, multi-card photos, fixes (unrounded grade, redraw resets, overlay). |
| 2026-10-13 | Moved to `nk7ghub/pkmon` (`index.html`). |
| 2026-10-13 | PR #1: gap-based split, batch review, stack "Check" flags, install button and icons, `[hidden]` rule, viewport meta. |
| 2026-10-13 | PR #2: `Visual` picture check (Café Master; Cynthia 178 vs 169), install button everywhere, stack limits. |
| 2026-10-13 | PR #3: back navigation (`Nav`), change-card flow (`openReplace` / `replaceItem` / `openReview`). |
| 2026-10-13 | **PR #4: scan speed.** The user saw 3 cards take 3–5 min with 2 "not found". Reproduced: old code + a card list that never loads = **268 s, 0/3 found** (the list download was retried for every card with a 45 s timeout, then fell back to slow searches). Fix: list downloaded once with % progress and stall guard; 4 OCR passes instead of 9 (smaller strips); picture check 4 s/image, 8 s overall, pool 24; TCGdex + pokemontcg.io in parallel; slow pokemontcg.io skipped; per-card timing shown. |

## Benchmarks (headless Chromium, user's Alcremie / Charizard ex / Umbreon VMAX photo)
Simulated slow network: pokemontcg.io hanging, TCGdex list 4 s, details 1.5 s, images 0.6 s.

| Case | Old | New |
|---|---|---|
| Card list loads | 60 s, 3/3 | **28 s**, 3/3 (Charizard ex 006 and Umbreon VMAX TG23 sure; Alcremie TG08 Check) |
| Card list never loads | 268 s, 0/3 | **~45 s**, 1/3 (Charizard ex as Check), others "not found" with a note |

The two "new" runs above ran alone; the 60 s old run shared the CPU with a new run, so it's somewhat inflated. Phone times depend on CPU; OCR is the largest share (~6 s per card in the container).

## Tested
- All in headless Chromium with recorded API responses; the container can't reach pokemontcg.io or TCGdex.
- Real Tesseract OCR on the user's photos: Pikachu V 157/172, Rayquaza VMAX TG20, and three 3-card photos. The mock "official" images were made from the user's photos with colour, blur and crop changes, so picture scores are optimistic.
- No JS errors; no sideways scroll at 360/400/1280 px; light/dark; exports; trade; binder; paste/drop; artifact mode; back navigation; change-card; Chrome installability.

## Known limits / next steps
- **Live APIs not exercised from the build container.** If the TCGdex `/cards` list is very slow on mobile data, recognition drops to the weaker fallback (see benchmark). Settings → "Download card list now" retries it.
- eBay has no free sold API, so it links to sold listings. Graded prices are model estimates. Price alerts fire only while the app is open.
- Grid layouts (2 rows of cards) aren't split; use one row per photo. No perspective (keystone) correction.
- **Phase 2 (not started):** a GitHub Action that precomputes picture fingerprints for all ~20k cards, so picture matching works without per-scan image downloads. Possible need for workflow write permission.
