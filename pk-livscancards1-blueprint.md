# pk-livscancards1 — prompt blueprint

Build a **single-file HTML PWA** that scans physical items with the camera or photos, identifies them against a public catalogue, grades their condition, compares live market prices and tracks a portfolio.

**Layout.** Glass header: back, brand, live/offline chip, currency, install, theme. One `<main>` with views: Scanner · Portfolio · Trade · Settings. Fixed bottom nav. Bottom sheets for details, change-item, review and help. No sideways scroll at 360 px.

**Design rules.** Colour tokens on `:root` for light and dark. Glassmorphism, ambient blobs, holo-tilt cards. Our own `[hidden]{display:none!important}`. The web version keeps doctype, charset and viewport; strip them for the artifact. Never append `null` to the DOM.

**Core classes.** `.glass .panel .stage .stage.live .hud .meters .result .pickgrid .pick .checkbar .tray .kpis .markets .mk .sheet .nav .chip .seg .prog .toast`.

**Catalogue.** A compact JSON list (id, number, name, secondary fields such as HP or attacks, picture URL), built from public data by a script in `tools/`, served from the app's own site, cached by version, loaded at startup.

**Scan pipeline.**
1. Input: native `<label for>` file inputs, paste, drop, blocked-picker help. Live camera: portrait 5:7 stage, aspect frame, corner brackets, hint.
2. `splitItems` at texture gaps (6 per photo, 30 photos).
3. `locateItem`: edges + aspect pair search; fallbacks for oversized parts (outer edges, outline, part width × aspect).
4. OCR: 3 number passes, name pass, full pass; 20 s per pass, 40 s per item; restart the worker on timeout.
5. Rank locally: exact/fuzzy ID, set size, trigram name, secondary fields, half-read long words, IDs in digit runs, previous-stage penalty, promo tie-break.
6. Picture check (colour grid + gradient hash), time-limited.
7. Decide: sure → add; unsure → add flagged Check; weak → pick grid only.
8. Price the top item (8 s), queue the rest. Show a ⏱ timing line.

**Market data.** Primary price API; fallback via set list → set items → item pricing; never overwrite a price with an empty one; record the source. Side-by-side markets, sold-listing links, graded estimates labelled, alerts, multi-currency.

**Portfolio.** KPIs, trend chart, grouped list, sealed items, set progress. Change-item keeps qty, cost and alerts.

**Platform.** `history` steps (double-Back exits), install prompt, iOS steps, service worker shell (skips the catalogue file). Artifact: vision sample, db, downloads, user. Exports: CSV, text, PDF, JSON; share links.

**Process.** Diagnose from screenshots → plan, risks, approval → build with live % → test real OCR on all past photos, mock no-price/429/hang → PR → artifact → `handoff.md`.
