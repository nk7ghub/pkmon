---
name: pk-livscancards1
description: Build or extend a live camera/photo scanner web app that identifies physical items (cards, labels, products, documents) against a public catalogue, grades condition, compares market prices and tracks a portfolio, as a single-file HTML PWA plus Claude artifact. Use for scan-and-price, card scanners, photo ID, OCR + picture matching, price comparison, or pk-livscancards1.
---

# pk-livscancards1

The reference build is `nk7ghub/pkmon` (`index.html`, `handoff.md`). In that repo, read `handoff.md` first and extend; never rebuild. For a new domain, reuse the patterns, not the data.

## Workflow
Plan, risk table, time/tokens → wait for go → build with a live % after each step → test → PR → update `handoff.md`. No silent plan changes.

## Patterns
- **Shell.** One file; light/dark tokens on `:root`; glass UI, bottom nav, sheets with Back. The web copy starts with doctype, charset and viewport (strip them for the artifact). Add our own `[hidden]{display:none!important}`.
- **Input.** Native `<label for>` file inputs (camera + gallery), paste, drop. If no blur within 1.5 s, the picker was blocked → show a help sheet.
- **Pipeline.**
  1. Split multi-item photos at texture gaps.
  2. Locate each item by edge continuity and aspect ratio.
  3. OCR a full-resolution crop with few small passes; stop at the first ID.
  4. Rank against a cached local catalogue index (ID, group size, trigram name).
  5. Picture check: colour grid + gradient hash.
  6. Fetch details from two sources in parallel.
  7. Above the "sure" threshold add it; otherwise show a pick grid.
- **Budgets.** Download the catalogue once with % and a stall guard, never per item. 4 s per image, 8 s per stage; skip slow sources for the session. Show a per-item timing line.
- **Correction.** Unsure items become best guesses flagged "Check". Change-item lists variants by picture match and keeps qty, cost and alerts.
- **Market data.** Side-by-side sources, deep links where there's no API, estimates labelled, multi-currency, alerts.
- **Platform.** One `history` step per view or sheet; double-Back exits. Install prompt, iOS steps, artifact → web link. The artifact has no network, camera or install: use vision `sample`, `db`, `downloads`, `user`.

## Testing
Headless Chromium with recorded APIs. Real Tesseract (npm) on the user's photos. Simulate a slow or hanging network and time old vs new. Check overflow, JS errors, installability.

## Don'ts
No invented prices, no user data, no unverified API claims.
