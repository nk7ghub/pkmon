# Handoff: PKmon Card Vault

Pokémon TCG card scanner, condition pre-grader, multi-market pricing and portfolio tracker, built as a single-file PWA.

Updated: 2026-10-14

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
| `pkmon-cards.json` | **Offline card list**: 20,635 English cards / 176 sets (number, name, HP, attack + ability names, "evolves from", rarity, picture). ~1.3 MB, ~347 KB gzipped. Built from the public `PokemonTCG/pokemon-tcg-data` repo (data date 2026-09-16). |
| `tools/build-cards.py` | Rebuilds `pkmon-cards.json`: `git clone --depth 1 https://github.com/PokemonTCG/pokemon-tcg-data /tmp/ptcg && python3 tools/build-cards.py /tmp/ptcg > pkmon-cards.json`, then set `CARDS_V` in `index.html` to the new `v`. |
| `pkmon-sw.js` | Service worker: offline app shell (`pkmon-shell-v4`), network-first, never caches API calls; leaves `pkmon-cards.json` to the app's own `pkmon-index` cache |
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
2. **Find the card.** `locateCard()` takes edge-continuity profiles plus a 63:88 pair search. In a multi-card photo, a box narrower than 72 % of the cut-out part is wrong (the artwork frame of a full-art card, or edges lost on textured cloth). Then, in order: `locateCard(part, true)` (edges searched only in the outer 30 %), `textureBox()` (outline against a plain background, any tilt), and finally the part's width with the 63:88 shape, centred. The grader gets the exact crop; OCR gets a slightly larger full-resolution crop.
3. **Grade.** `Grader.analyze`: centering from border widths (PSA 55/45 = 10); corners and edges from whitening and straightness; surface from fine lines and glare. `Foil` tracks shimmer between frames.
4. **Read text.** `Scan.ocrRead`: up to 3 number passes (the ones that found numbers in testing; stop at the first parse), 2 name passes, 1 full-card pass (1100 px). Each pass has a 20 s limit and the card a 40 s budget; a pass that runs over **restarts the reader** (otherwise later cards queue behind it and all fail with "Reading the card took too long"). `parseCardNumber` / `numberCandidates` handle `057/195`, `TG20/TG30`, `GG35/GG70`, `SV107/SV122` and noise like `1157/1725`. Name candidates skip "Evolves from X".
5. **Card list.** `CardIndex.load()` reads `pkmon-cards.json` from the app's own site (starts at app launch, before the online check), keeps it in Cache Storage `pkmon-index` keyed by `CARDS_V`, single flight. After a failure it waits 60 s before trying again, so cards in a stack never each wait. No outside server is needed to match a card.
6. **Read extras.** `ocrRead` also returns `names` (words near the name in reading order, "Evolves from …" removed), `hps` (round numbers 30–340 in the name strip), and `evo` (the "Evolves from" name).
7. **Rank.** `CardIndex.rank`: exact number +45, set size +25, fuzzy number pair +65, trigram name up to +40 plus up to +10 evidence; VMAX/VSTAR ±, and a capital "V" right after the name ("giaragoVs") favours "… V" cards. Attack/ability names: exact, or half-read for names of 8+ letters (≥ 70 % of trigrams, ≥ 60 % on an already-named card): +25 / +20 / +8. Number hidden in a digit run ("18371551" → 183): +15, or +35 when the set size follows. Promo sets −3 on ties. Only for cards already at ≥ 20: HP match +12, attack/ability name in the text +20 (+8 each extra), "evolves from" match +12, and −18 for the card named in "Evolves from" (it's the *previous* stage: Shaymin V vs Shaymin VSTAR). A strong read keeps the top 12; a weak read (< 60) keeps 20; same-name prints are added up to 28.
8. **Picture check.** `Visual`: 8×11 colour grid plus 16×16 gradient hash vs each candidate's official image (`images.pokemontcg.io`). Up to +45, relative within the pool; 4 s per image, 8 s in total.
9. **Decide.** "Sure" = score ≥ 90 with a lead ≥ 12, or ≥ 65 with a lead ≥ 25 (never from a weak-read pool). Below 50 the scan is "weak": it shows the pick grid and is **not** added automatically, even in stack mode. Otherwise unsure cards in stack mode are added as the best guess with `item.check = true`.
10. **Prices.** `detailsFor` asks pokemontcg.io for the first card only, 8 s at most; if that times out, pokemontcg.io is skipped for 5 min (`ENV.ptcgSlowUntil`). **If pokemontcg.io returns no price, an error or 429** (the $0 cards of 2026-10-14), `dexPrices()` gets the price from TCGdex using only endpoints the app has always relied on: `dexFindCard()` matches the set by name (gallery subsets like "Brilliant Stars Trainer Gallery" fold into the main set; id fallbacks `sv2→sv02`, `sv3pt5→sv03.5`), reads `/sets/{id}` for the card with the same number (`normNum`, so `014` = `14`) and name, then `/cards/{id}` for pricing. Older name + number search is the last resort. The price's source is saved (`prices.via`) and shown on the detail page. `hasPrice()` decides. `PriceQueue` and `refreshPrices` use the same fallback, and a refresh never overwrites a price with an empty one. Other choices are built from the list (`CardIndex.toCard`). Any card saved without prices goes into `PriceQueue`, which fetches prices in one batch 1.5 s later.
11. **Without the card list** (rare): pokemontcg.io search by number, then by each name word, then TCGdex, each with a time limit, and the note says the list didn't load.
12. **Timing.** Every result has `timing` ("10.5 s · read 10.0 s · pictures 0.0 s · prices 0.4 s"), shown under each result (⏱) and logged to the console.

## Live camera
`Scan.guide()` is an upright 63:88 frame (90 % of the stage height). While the camera runs, the stage gets class `live` (aspect 5:7), with white corner brackets and the hint "Card upright · fill the frame". The phone's own camera ("Take photo") can't show a guide; use "Live camera" for it.

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

| 2026-10-13 | **Rollback (user request):** `index.html` restored to `e184dea` (after PR #2, before PR #3), the version the user found scanned best. Removed by this rollback: back navigation (`Nav`), change-card (`openReplace` / `replaceItem` / `openReview`), and the PR #4 speed changes (card-list single download, 4 OCR passes, budgets, timing line). Kept: blueprint, skill, review, handoff. Re-apply later one change at a time, testing on the phone after each. |
| 2026-10-14 | **PR #10: prices fixed properly.** New scans (Lugia V, Raichu V, Charizard VSTAR, Flareon TG01) still showed $0: pokemontcg.io returned no prices (or a rate limit), and the TCGdex backup from PR #8 used an unverified `name=eq:` search. Now: set list → set cards → card pricing, tested with TCGdex-style ids (padded numbers, `sv02`, gallery cards inside the main set) for no-price and 429 cases. Also fixed a stray "null" under single-card results. |
| 2026-10-14 | **PR #9: 3-card reliability + live guide.** User photo Urshifu VMAX TG19 · Urshifu VMAX TG29 · Duraludon VMAX TG30: cards 2–3 "took too long" (a timed-out pass kept the reader busy, so the next cards queued behind it) and the box finder lost card edges on grey cloth. Fix: reader restart on timeout, 40 s card budget, 3 number passes instead of 6, outer-edge / 63:88 cut-out fallbacks, portrait live-camera frame. Test: this photo 2/3 on top (TG29 right, Duraludon another print marked Check, TG19 wrong); 20–35 % faster per card; earlier photos unchanged. |
| 2026-10-14 | **PR #8: full-art cut-out, half-read attacks, TCGdex prices.** User photo Regidrago V 183/195 · Magearna V 182/195 · Squawkabilly ex 169/193: Regidrago became "Roark" because the box finder cut the artwork frame; all three showed $0 because pokemontcg.io returned no price. Fix: `textureBox` fallback, fuzzy attack names, digit-run numbers, "V" suffix, promo tie-break, TCGdex price fallback, ⏱ line on its own row. |
| 2026-10-14 | **Offline card list + back button (PR #7).** Cause of slow and wrong scans: the TCGdex `/cards` list download (retried per card, 45 s each) and, without it, a backup search using the *longest* word read ("ShayminV", "Chaomedeon"). Fix: `pkmon-cards.json` shipped with the app; ranking uses HP, attack names and "evolves from" from the list; prices only for the shown card; weak guesses not auto-added; per-card timing. Back navigation and change-card (PR #3) re-applied unchanged. |

## Benchmarks (2026-10-14, headless Chromium, real Tesseract, real card list)
No card pictures in the test (images can't be reached from the build container), so these are text-only results; live, the picture check adds up to +45 to the right print.

| Photo | Old (e184dea) | New |
|---|---|---|
| Alcremie TG08 · Charizard ex 006/165 · Umbreon VMAX TG23 | on the phone: 3–5 min, 1/3 (and the wrong Alcremie) | **35 s, 3/3** (Charizard sure; Alcremie, Umbreon "Check": same art in two sets) |
| Same photo, pokemontcg.io hanging | 268 s, 0/3 (simulated) | **~33 s, 3/3**, prices filled in later |
| Octillery TG03 · Acerola's Premonition TG24 · Gloria TG26 | — | 29 s, 3/3 (2 sure) |
| Rayquaza VMAX TG20 / Pikachu V 157/172 | — | 7 s / 9 s, both sure |
| Café Master TG25 · Cynthia's Ambition 178 · 169 | — | 2/3 by text (Cynthia prints tie; picture decides live); Café Master's name wasn't readable, so it's a pick, not a guess |
| Shaymin VSTAR (the phone's read text) | not recognised | Shaymin VSTAR 014 / 173 (both prints, picture decides) |
| Regidrago V 183 · Magearna V 182 · Squawkabilly ex 169 (PR #8) | Roark (wrong), $0 ×3 | Regidrago V 183 (Check), Magearna V 182 sure, Squawkabilly ex (Check: number not read in the test, so same-art prints tie); prices from TCGdex when pokemontcg.io has none |

After PR #8 the whole set of photos is 15 cards, 14 right on top by text alone, ~7–11 s per card. Café Master TG25 is now found too (better cut-out).

Most of the time is reading text (~6–13 s per card in the container; phones vary).

## Tested
- All in headless Chromium with recorded API responses; the container can't reach pokemontcg.io or TCGdex.
- Real Tesseract OCR on the user's photos: Pikachu V 157/172, Rayquaza VMAX TG20, and three 3-card photos. The mock "official" images were made from the user's photos with colour, blur and crop changes, so picture scores are optimistic.
- No JS errors; no sideways scroll at 360/400/1280 px; light/dark; exports; trade; binder; paste/drop; artifact mode; back navigation; change-card; Chrome installability.

## Known limits / next steps
- **Gold / full-art foil names** (e.g. Single Strike Urshifu VMAX on gold) are often unreadable for Tesseract. Matching then relies on attack names, "evolves from", HP and the picture check. A real fix needs better recognition (e.g. precomputed picture fingerprints, Phase 2).
- **Live APIs not exercised from the build container.** Matching now works without them; prices and the picture check still need pokemontcg.io / images.pokemontcg.io. If that image host ever blocks reading pixels (CORS), the picture check silently adds nothing.
- **New sets** released after the card list date (2026-09-16) aren't in `pkmon-cards.json`; rebuild with `tools/build-cards.py`. A GitHub Action could do this weekly.
- eBay has no free sold API, so it links to sold listings. Graded prices are model estimates. Price alerts fire only while the app is open.
- Grid layouts (2 rows of cards) aren't split; use one row per photo. No perspective (keystone) correction.
- **Phase 2 (not started):** a GitHub Action that precomputes picture fingerprints for all ~20k cards, so picture matching works without per-scan image downloads. Possible need for workflow write permission.
