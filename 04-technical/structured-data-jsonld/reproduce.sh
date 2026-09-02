#!/usr/bin/env bash
# What can a schema.org / JSON-LD parser extract from each page?
# We pull every <script type="application/ld+json"> block out of the HTML,
# parse it as JSON, and count (a) typed entities — objects carrying an @type —
# and (b) typed facts — property assertions made about those typed entities.
# No network, no browser, no LLM, no randomness. Pure python3 stdlib.
set -euo pipefail
cd "$(dirname "$0")"

count() {
  python3 - "$1" <<'PY'
import sys, re, json

html = open(sys.argv[1], encoding="utf-8").read()

# Grab the contents of every application/ld+json script block.
blocks = re.findall(
    r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    html, re.IGNORECASE | re.DOTALL)

entities = 0   # objects that carry an @type
facts = 0      # property assertions on typed objects (keys other than @context/@type)

def walk(node):
    global entities, facts
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

print(f"{entities} {facts}")
PY
}

printf '%-8s %-16s %-16s\n' "VARIANT" "TYPED ENTITIES" "TYPED FACTS"
for variant in before after; do
  read -r ents fcts < <(count "$variant/index.html")
  printf '%-8s %-16s %-16s\n' "$variant" "$ents" "$fcts"
done

echo
echo "before/ ships no JSON-LD: a schema.org parser extracts nothing structured."
echo "after/ ships the same visible article plus JSON-LD: the parser reads typed facts."
