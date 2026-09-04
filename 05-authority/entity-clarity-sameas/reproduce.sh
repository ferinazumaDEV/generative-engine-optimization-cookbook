#!/usr/bin/env bash
# How many named entities on the page resolve UNAMBIGUOUSLY to a canonical ID?
# We parse the JSON-LD from each page and, for every entity in "about", count the
# distinct canonical Wikidata Q-IDs it declares (via @id or sameAs). An entity is
# "unambiguously resolved" when that set has exactly one member: a plain name with
# no canonical link resolves to nothing (0); a name backed by one Wikidata ID
# resolves to exactly one real-world thing (1). No network, no browser, no LLM.
#
# Usage: bash reproduce.sh [--json]
#   (no flag)  human-readable table, unchanged
#   --json     the same numbers as JSON on stdout, for dataset/build.sh
set -euo pipefail
cd "$(dirname "$0")"

JSON=0
for arg in "$@"; do
  [ "$arg" = "--json" ] && JSON=1
done

python3 - "$@" <<'PY'
import json, re, sys, pathlib

# Canonical identifier: a Wikidata item URL. This is the strongest machine-checkable
# anchor; Wikipedia URLs in sameAs corroborate it but a Wikidata Q-ID is the key.
WIKIDATA = re.compile(r'https?://(?:www\.)?wikidata\.org/(?:wiki|entity)/(Q\d+)')

def jsonld_blocks(html):
    return re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, flags=re.I | re.S)

def entities(html):
    out = []
    for block in jsonld_blocks(html):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        for node in (data if isinstance(data, list) else [data]):
            about = node.get("about") if isinstance(node, dict) else None
            if isinstance(about, dict):
                about = [about]
            if isinstance(about, list):
                out.extend(e for e in about if isinstance(e, dict))
    return out

def canonical_ids(entity):
    """Distinct Wikidata Q-IDs declared by this entity, from @id and sameAs."""
    refs = []
    if isinstance(entity.get("@id"), str):
        refs.append(entity["@id"])
    same = entity.get("sameAs", [])
    refs.extend([same] if isinstance(same, str) else [s for s in same if isinstance(s, str)])
    ids = set()
    for r in refs:
        m = WIKIDATA.search(r)
        if m:
            ids.add(m.group(1))
    return ids

def score(path):
    html = pathlib.Path(path).read_text(encoding="utf-8")
    ents = entities(html)
    resolved = sum(1 for e in ents if len(canonical_ids(e)) == 1)
    return len(ents), resolved

rows = []
for variant, desc in (("before", "names only, no IDs"),
                      ("after",  "names + sameAs (Wikidata)")):
    total, resolved = score(f"{variant}/index.html")
    rows.append({"variant": variant, "structured_data": desc,
                 "entities": total, "entities_resolved": resolved})

if "--json" in sys.argv[1:]:
    json.dump({
        "technique": "entity-clarity-sameas",
        "chapter": "05-authority",
        "handbook_section": "docs/05-authority.md",
        "title": "Entity clarity: disambiguate with sameAs + canonical IDs",
        "method": "deterministic-offline",
        "requires_llm": False,
        "requires_network": False,
        "measurements": [
            {"id": "entities_resolved", "role": "primary",
             "metric": "named entities resolved to exactly one canonical Wikidata Q-ID via @id or sameAs",
             "unit": "entities",
             "before_value": rows[0]["entities_resolved"],
             "after_value": rows[1]["entities_resolved"]},
            {"id": "entities", "role": "denominator",
             "metric": "named entities the page declares in its about list",
             "unit": "entities",
             "before_value": rows[0]["entities"],
             "after_value": rows[1]["entities"]},
        ],
        "table": rows,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0)

print(f'{"VARIANT":<8} {"STRUCTURED DATA":<30} {"ENTITIES":>8} {"RESOLVED TO A CANONICAL ID":>28}')
for r in rows:
    print(f'{r["variant"]:<8} {r["structured_data"]:<30} {r["entities"]:>8} {r["entities_resolved"]:>28}')
PY

if [ "$JSON" -eq 0 ]; then
  echo
  echo "Both pages show the same article to a human."
  echo "Only the 'after' page lets a machine pin each name to exactly one real-world thing."
fi
