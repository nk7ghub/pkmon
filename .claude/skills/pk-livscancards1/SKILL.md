---
name: pk-livscancards1
description: Build or extend a live camera/photo scanner web app that identifies physical items (cards, labels, products, documents) against a public catalogue, grades condition, compares market prices and tracks a portfolio, as a single-file HTML PWA plus Claude artifact. Use for scan-and-price, card scanners, photo ID, OCR + picture matching, price comparison, or pk-livscancards1.
---

# pk-livscancards1

Reference build: `nk7ghub/pkmon` (`index.html`, `handoff.md`). There, read `handoff.md` first and extend; never rebuild. New domain: reuse patterns, not data.

## Workflow
Diagnose from screenshots → plan, risks, time/tokens → wait for go → build with live % → test on real photos → PR, merge, republish artifact → update `handoff.md`. No silent plan changes. If old photos get worse, revert that part.

## Patterns
- **Shell.** One file, light/dark tokens, glass UI, bottom nav, sheets with Back. Strip doctype/charset/viewport for the artifact. `append(null)` prints "null": pass `""`.
- **Catalogue.** Ship it as compact JSON built from public data by a script; load once from your own site, cache, version. Never fetch per item; back off after failure.
- **Pipeline.**
  1. Split photos at texture gaps.
  2. Locate by edges + aspect ratio. If the box is much smaller than the split part, fall back: outer edges → outline → part width × aspect.
  3. OCR: few passes, each with a time limit, plus an item budget. Restart the worker on timeout, or later items queue and fail.
  4. Rank locally: ID, set size, trigram name, HP, attack names, "evolves from". Half-read long words count; IDs hide in digit runs; promos lose ties.
  5. Picture check, time-limited.
  6. Price only the shown item.
- **Decide.** Sure thresholds, else a pick grid. Weak scores never auto-add; unsure ones get "Check". Show per-item timing.
- **Prices.** Primary source, then a fallback through stable endpoints (set list → set items → item), never guessed query syntax. Never overwrite a price with an empty one; queue missing prices; show the source.
- **Platform.** One `history` step per view; double-Back exits. Live camera: portrait stage, aspect frame, corner brackets, hint. Install prompt. Artifact: vision `sample`, `db`, `downloads`, `user`. Warn on downloaded copies.

## Testing
Headless Chromium, real OCR, real catalogue. Mock APIs in the other database's id style, including no-price, rate-limit (429) and hang cases. Rerun all past photos before merging; dump crops when OCR fails. Check overflow, errors, Back.

## Don'ts
No invented prices, no user data, no unverified API claims or query syntax.
