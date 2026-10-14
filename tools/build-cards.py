#!/usr/bin/env python3
"""Build pkmon-cards.json (the scanner's offline card list) from a clone of
https://github.com/PokemonTCG/pokemon-tcg-data.

  git clone --depth 1 https://github.com/PokemonTCG/pokemon-tcg-data /tmp/ptcg
  python3 tools/build-cards.py /tmp/ptcg > pkmon-cards.json
"""
import json, glob, os, subprocess, sys

src = sys.argv[1]
sets = sorted(json.load(open(os.path.join(src, "sets/en.json"))), key=lambda s: s["releaseDate"])
try:
    ver = subprocess.check_output(["git", "-C", src, "log", "-1", "--format=%cs"], text=True).strip()
except Exception:
    ver = max(s["releaseDate"] for s in sets).replace("/", "-")

# row: [set index, number, name, hp, abilities|attacks, evolves from, rarity, image kind?, id if not <set>-<number>?]
# image url kinds: 0 = images.pokemontcg.io/<set>/<number>.png, 1 = images.scrydex.com/pokemon/<id>/small, else the full url
def img_kind(c, sid):
    small = c["images"]["small"]
    if small == f"https://images.pokemontcg.io/{sid}/{c['number']}.png": return 0
    if small == f"https://images.scrydex.com/pokemon/{c['id']}/small": return 1
    return small

out_sets, out_cards = [], []
for i, s in enumerate(sets):
    out_sets.append([s["id"], s["name"], s.get("series", ""), s.get("printedTotal"), s.get("total"), s["releaseDate"]])
    path = os.path.join(src, "cards/en", s["id"] + ".json")
    if not os.path.exists(path): continue
    for c in json.load(open(path)):
        moves = [a["name"] for a in c.get("abilities", [])] + [a["name"] for a in c.get("attacks", [])]
        hp = int(c["hp"]) if str(c.get("hp", "")).isdigit() else 0
        row = [i, c["number"], c["name"], hp, "|".join(moves), c.get("evolvesFrom", ""), c.get("rarity", "")]
        k = img_kind(c, s["id"])
        odd_id = c["id"] != f"{s['id']}-{c['number']}"
        if k or odd_id: row.append(k)
        if odd_id: row.append(c["id"])
        out_cards.append(row)

json.dump({"v": ver, "src": "PokemonTCG/pokemon-tcg-data", "sets": out_sets, "cards": out_cards},
          sys.stdout, ensure_ascii=False, separators=(",", ":"))
