#!/usr/bin/env python3
"""Build pkmon-fp.bin: a picture fingerprint for every card in pkmon-cards.json, same order.

  pip install pillow numpy
  python3 tools/build-fingerprints.py pkmon-cards.json pkmon-fp.bin

Fingerprint (must match FP.feat in index.html):
  card image → 256×352 RGB → 4×4 box average → 64×88
  colour: 4 cols × 8 rows cells (16×11 px), each channel ÷ the card's channel mean, ×100, capped at 255 → 96 bytes
  shape: 9×8 cell means of grey (.299R+.587G+.114B); bit = cell[c] > cell[c+1]; row r → byte r, bit c
         artwork x 5..59, y 9..41 (8 bytes) and whole card x 1..64, y 0..88 (8 bytes)
  flag: 1 = built, 0 = image missing
File: b"PKFP", version (1 byte), record size (1 byte), count (uint32 LE), card list version (16 bytes ASCII), records.
"""
import io, json, struct, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image

REC = 113

def img_url(row, sets):
    st = sets[row[0]]; lid = row[1]; ik = row[7] if len(row) > 7 else 0
    cid = row[8] if len(row) > 8 else f"{st[0]}-{lid}"
    if ik == 1: return f"https://images.scrydex.com/pokemon/{cid}/small"
    if isinstance(ik, str) and ik: return ik
    return f"https://images.pokemontcg.io/{st[0]}/{lid}.png"

def cells(a, x0, y0, x1, y1, nx, ny):
    sub = a[y0:y1, x0:x1]; h, w = sub.shape[:2]
    return sub.reshape(ny, h // ny, nx, w // nx, *sub.shape[2:]).mean(axis=(1, 3))

def dhash(grey, x0, y0, x1, y1):
    g = cells(grey, x0, y0, x1, y1, 9, 8)
    out = bytearray(8)
    for r in range(8):
        b = 0
        for c in range(8):
            if g[r, c] > g[r, c + 1]: b |= 1 << c
        out[r] = b
    return bytes(out)

def feat(im):
    a = np.asarray(im.convert("RGB").resize((256, 352), Image.BILINEAR), dtype=np.float64)
    a = a.reshape(88, 4, 64, 4, 3).mean(axis=(1, 3))          # 64×88
    m = a.reshape(-1, 3).mean(axis=0); m[m == 0] = 1
    col = cells(a, 0, 0, 64, 88, 4, 8) / m                    # 8 rows × 4 cols × 3
    colb = bytes(np.clip(np.rint(col * 100), 0, 255).astype(np.uint8).reshape(-1))
    grey = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    return colb + dhash(grey, 5, 9, 59, 41) + dhash(grey, 1, 0, 64, 88) + b"\x01"

def fetch(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pkmon-fingerprints/1 (+https://github.com/nk7ghub/pkmon)"})
            with urllib.request.urlopen(req, timeout=30) as r: return r.read()
        except Exception:
            time.sleep(1.5 * (k + 1) ** 2)
    return None

def main():
    data = json.load(open(sys.argv[1])); out = sys.argv[2]
    sets, cards = data["sets"], data["cards"]
    urls = [img_url(r, sets) for r in cards]
    recs = [None] * len(cards); missing = []
    def job(i):
        raw = fetch(urls[i])
        try: recs[i] = feat(Image.open(io.BytesIO(raw))) if raw else None
        except Exception: recs[i] = None
        if recs[i] is None: missing.append(urls[i])
    t0 = time.time()
    with ThreadPoolExecutor(16) as ex:
        for n, _ in enumerate(ex.map(job, range(len(cards)))):
            if n % 1000 == 0: print(f"{n}/{len(cards)}  {time.time() - t0:.0f}s  missing {len(missing)}", flush=True)
    with open(out, "wb") as f:
        f.write(b"PKFP" + bytes([1, REC]) + struct.pack("<I", len(cards)) + data["v"].encode()[:16].ljust(16, b"\0"))
        for r in recs: f.write(r if r else b"\0" * REC)
    print(f"done {len(cards)} cards, {len(missing)} missing, {time.time() - t0:.0f}s")
    for u in missing[:20]: print("  missing", u)
    if len(missing) > len(cards) * .2: sys.exit("too many images missing")

if __name__ == "__main__": main()
