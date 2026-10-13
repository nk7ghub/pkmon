# pk-livscancards1 — prompt blueprint

Build a **single-file HTML PWA** that scans physical items with the camera or photos, identifies them against a public catalogue, grades their condition, compares live market prices and tracks a portfolio.

**Layout.** Glass header: back, brand, live/offline chip, currency, install, theme. One `<main>` with views: Scanner · Portfolio · Trade · Settings. Fixed bottom nav. Bottom sheets for details, change-item, review and help. Mobile-first; no sideways scroll at 360 px.

**Design rules.** Colour tokens on `:root`, with light and dark. Glassmorphism (`.glass`, blur, inset highlights), slow ambient blobs, holo-tilt cards. Display, body and mono fonts. `[hidden]{display:none!important}` in our own CSS. Doctype, charset and viewport for the web version; strip them for the artifact.

**Core classes.** `.glass .panel .stage .hud .meters .result .pickgrid .pick .checkbar .tray .kpis .markets .mk .sheet .sheet-top .nav .chip .seg .switch .prog .toast`.

**Scan pipeline.**
1. Input: native `<label for>` file inputs (camera + gallery); paste, drop; blocked-picker detector → help sheet.
2. `splitItems`: per-column texture profile → gaps, cut over-wide parts; limits 6 per photo, 30 photos.
3. `locateItem`: edge-continuity profiles + known aspect-ratio pair search.
4. `grade`: centering ratios, corners and edges (whitening, straightness), surface (lines, glare).
5. OCR: up to 4 number passes (stop at first parse), name pass, one full pass. Parse IDs with noise-tolerant regex plus candidate pairs.
6. Local catalogue index: streamed with %, cached 7 days, single flight, stall guard.
7. Rank: exact ID, set size, trigram name, suffix rules. Weak read → wider pool.
8. Picture check: colour grid + gradient hash vs catalogue images, with time budgets.
9. Details: two sources in parallel, slow source skipped.
10. Decide: "sure" thresholds, else pick grid; stack mode adds best guesses flagged Check.
11. Per-item timing line.

**Market data.** Side-by-side market cards (low / mid / market / high, trend, 1/7/30-day averages). Sold-listing deep links. Raw vs graded toggle using model multipliers labelled *estimate*. Alerts. Multi-currency with live rates and a fallback table.

**Portfolio.** KPIs, SVG trend (snapshots + averages), grouped list, sealed/manual items, set progress. Change-item keeps qty, cost and alerts.

**Platform.** Back navigation through `history` steps (double-Back exits). Install prompt; iOS steps; artifact → web link. Service worker shell. Artifact capabilities: vision sample, db, downloads, user. Exports: CSV, text, PDF, JSON; share links.

**Process.** Plan, risks, approval → build with live % → test real OCR in headless Chromium → PR → handoff.md.
