#!/usr/bin/env bash
# What can a schema.org / JSON-LD parser extract from each page?
# We pull every <script type="application/ld+json"> block out of the HTML,
# parse it as JSON, and count (a) typed entities — objects carrying an @type —
# and (b) typed facts — property assertions made about those typed entities.
# No network, no browser, no LLM, no randomness. Pure python3 stdlib.
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
import json, re, sys

def count(path):
    html = open(path, encoding="utf-8").read()

    # Grab the contents of every application/ld+json script block.
    blocks = re.findall(
        r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.IGNORECASE | re.DOTALL)

    entities = 0   # objects that carry an @type
    facts = 0      # property assertions on typed objects (keys other than @context/@type)

    def walk(node):
        nonlocal entities, facts
        if isinstance(node, dict):
            if "@type" in node:
                entities += 1
                facts += sum(1 for k in node if k not in ("@context", "@type"))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for raw in blocks:
        walk(json.loads(raw))

    return entities, facts

rows = []
for variant, has_jsonld in (("before", "no"), ("after", "yes")):
    ents, fcts = count(f"{variant}/index.html")
    rows.append({"variant": variant, "jsonld_present": has_jsonld,
                 "typed_entities": ents, "typed_facts": fcts})

if "--json" in sys.argv[1:]:
    json.dump({
        "technique": "structured-data-jsonld",
        "chapter": "04-technical",
        "handbook_section": "docs/04-technical.md",
        "title": "Structured data (JSON-LD): make your facts machine-readable",
        "method": "deterministic-offline",
        "requires_llm": False,
        "requires_network": False,
        "measurements": [
            {"id": "typed_facts", "role": "primary",
             "metric": "typed facts a JSON-LD/schema.org parser extracts (keys other than @context/@type on a typed object)",
             "unit": "typed facts",
             "before_value": rows[0]["typed_facts"],
             "after_value": rows[1]["typed_facts"]},
            {"id": "typed_entities", "role": "secondary",
             "metric": "typed entities a JSON-LD/schema.org parser extracts (objects carrying an @type)",
             "unit": "typed entities",
             "before_value": rows[0]["typed_entities"],
             "after_value": rows[1]["typed_entities"]},
        ],
        "table": rows,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0)

print('%-8s %-16s %-16s' % ("VARIANT", "TYPED ENTITIES", "TYPED FACTS"))
for r in rows:
    print('%-8s %-16s %-16s' % (r["variant"], r["typed_entities"], r["typed_facts"]))
PY

if [ "$JSON" -eq 0 ]; then
  echo
  echo "before/ ships no JSON-LD: a schema.org parser extracts nothing structured."
  echo "after/ ships the same visible article plus JSON-LD: the parser reads typed facts."
fi
