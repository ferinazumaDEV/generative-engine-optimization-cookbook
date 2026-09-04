#!/usr/bin/env bash
# How many claims in a document carry an inline, linkable source right next to them?
# A claim with an adjacent linkable source is a claim->source PAIR: the unit an
# extractor can lift as "this assertion, backed by that URL". This counts those
# pairs in each variant's document SOURCE. No network, no browser, no LLM.
#
# Usage: bash reproduce.sh [--json]
#   (no flag)  human-readable table, unchanged
#   --json     the same numbers as JSON on stdout, for dataset/build.sh
set -euo pipefail
cd "$(dirname "$0")"

python3 - "$@" <<'PY'
import json, re, sys

# A "claim" = a markdown list item inside the <!-- claims:start --> / :end block.
# A "source" = an inline linkable reference adjacent to that claim, i.e. a
# markdown link with an http(s) URL on the same line: [text](https://...).
# A claim->source PAIR is one claim line that contains >= 1 such source.
CLAIM_LINE = re.compile(r'^\s*[-*]\s+\S')
INLINE_LINK = re.compile(r'\]\((https?://[^)\s]+)\)')

def analyze(path):
    text = open(path, encoding="utf-8").read()
    m = re.search(r'<!--\s*claims:start\s*-->(.*?)<!--\s*claims:end\s*-->', text, re.S)
    block = m.group(1) if m else text
    claims = 0
    sourced = 0
    for line in block.splitlines():
        if CLAIM_LINE.match(line):
            claims += 1
            if INLINE_LINK.search(line):
                sourced += 1
    return claims, sourced

results = {}
for variant in ("before", "after"):
    results[variant] = analyze(f"{variant}/article.md")

if "--json" in sys.argv[1:]:
    rows = [{"variant": variant,
             "document": doc,
             "claims": results[variant][0],
             "claim_source_pairs": results[variant][1]}
            for variant, doc in (("before", "unsourced"),
                                 ("after", "citation-anchored"))]
    json.dump({
        "technique": "citation-anchoring",
        "chapter": "06-measurement",
        "handbook_section": "docs/06-measurement.md",
        "title": "Citation anchoring: put a linkable source next to every claim",
        "method": "deterministic-offline",
        "requires_llm": False,
        "requires_network": False,
        "measurements": [
            {"id": "claim_source_pairs", "role": "primary",
             "metric": "claim-to-source pairs a deterministic parser extracts (a claim line carrying an inline http(s) link)",
             "unit": "claim-source pairs",
             "before_value": rows[0]["claim_source_pairs"],
             "after_value": rows[1]["claim_source_pairs"]},
            {"id": "claims", "role": "denominator",
             "metric": "claims inside the marked claims block",
             "unit": "claims",
             "before_value": rows[0]["claims"],
             "after_value": rows[1]["claims"]},
        ],
        "table": rows,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0)

print(f'{"VARIANT":<8} {"CLAIMS":<8} {"CLAIM->SOURCE PAIRS":<22}')
for variant in ("before", "after"):
    claims, sourced = results[variant]
    print(f'{variant:<8} {claims:<8} {sourced:<22}')

print()
print(f'before (unsourced doc): {results["before"][1]} claim->source pairs')
print(f'after  (anchored doc):  {results["after"][1]} claim->source pairs')
PY
