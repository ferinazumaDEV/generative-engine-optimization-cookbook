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
# Code is quoted, not asserted: fenced blocks are skipped and inline code spans
# are ignored. An image embed (![alt](url)) is not a source.
CLAIM_LINE = re.compile(r'^\s*[-*]\s+\S')
INLINE_LINK = re.compile(r'(?<!!)\[[^\]]*\]\((https?://[^)\s]+)\)')
CODE_SPAN = re.compile(r'`[^`\n]*`')
FENCE = re.compile(r'^\s*(```|~~~)')

def analyze(path):
    text = open(path, encoding="utf-8").read()
    m = re.search(r'<!--\s*claims:start\s*-->(.*?)<!--\s*claims:end\s*-->', text, re.S)
    block = m.group(1) if m else text
    claims = 0
    sourced = 0
    in_fence = False
    for line in block.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if CLAIM_LINE.match(line):
            claims += 1
            if INLINE_LINK.search(CODE_SPAN.sub('', line)):
                sourced += 1
    return claims, sourced

# --- Integrity check: do same-document fragment links land anywhere? ---------
# Separate from the pair count, which is published and never redefined. A pair
# is a claim with an http(s) link; this asks something the pair count cannot:
# when a claim links INTO this document (`[text](#id)`), does the target exist?
# It matters as soon as a pipeline resolves relative hrefs against the page URL
# before counting pairs: `#missing` becomes `https://site/page#missing` and
# scores as a source. Run this on the hrefs AS WRITTEN, before resolving them;
# afterwards a same-document fragment looks like any other URL.
#
# Resolution follows the HTML Standard's "find a potential indicated element":
# an element whose id is the fragment, or an <a> whose name is; the fragment is
# tried as written and then percent-decoded; `#` and `#top` (any case) are the
# top of the document even with no such element. Ids are case-sensitive. An id
# declared more than once is flagged: ids must be unique, so a citation that
# points at one has no single target. Fragments into OTHER documents cannot be
# checked offline and are not counted. Code is quoted, not markup: ids inside
# fenced blocks or inline code are not elements.
FRAGMENT_LINK = re.compile(r'(?<!!)\[[^\]]*\]\((#[^)\s]*)\)')
TAG = re.compile(r'<([A-Za-z][A-Za-z0-9-]*)(\s[^<>]*)?>')
ATTR = re.compile(r"(?<![\w:.-])(id|name)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'=<>`]+))")

def _outside_code(text):
    kept, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(CODE_SPAN.sub('', line))
    return kept

def unresolved_fragments(path):
    from urllib.parse import unquote
    text = open(path, encoding="utf-8").read()
    targets = {}
    for line in _outside_code(text):
        for tag in TAG.finditer(line):
            for a in ATTR.finditer(tag.group(2) or ''):
                attr, value = a.group(1), next(v for v in a.group(2, 3, 4) if v is not None)
                if attr == 'name' and tag.group(1).lower() != 'a':
                    continue
                targets[value] = targets.get(value, 0) + 1
    m = re.search(r'<!--\s*claims:start\s*-->(.*?)<!--\s*claims:end\s*-->', text, re.S)
    block = m.group(1) if m else text
    links = unresolved = 0
    for line in _outside_code(block):
        if not CLAIM_LINE.match(line):
            continue
        for href in FRAGMENT_LINK.findall(line):
            links += 1
            fragment = href[1:]
            if fragment == '' or unquote(fragment).lower() == 'top':
                continue
            if targets.get(fragment, 0) == 1 or targets.get(unquote(fragment), 0) == 1:
                continue
            unresolved += 1
    return links, unresolved

results = {}
for variant in ("before", "after"):
    results[variant] = analyze(f"{variant}/article.md")
fragments = {variant: unresolved_fragments(f"{variant}/article.md")
             for variant in ("before", "after")}

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
        # Not a measurement of the technique, so not in "measurements" (and
        # not in the dataset): an integrity check on the primary number. It
        # says how many claim links point into this document at an id that is
        # missing or declared twice. On both fixtures it is 0.
        "checks": [
            {"id": "unresolved_fragment_links",
             "metric": "links on claim lines that point at a fragment of this same document whose target is missing or declared more than once",
             "unit": "links",
             "fragment_links": {v: fragments[v][0] for v in ("before", "after")},
             "before_value": fragments["before"][1],
             "after_value": fragments["after"][1]},
        ],
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
print()
print('integrity check (not part of the pair count):')
for variant in ("before", "after"):
    links, unresolved = fragments[variant]
    print(f'{variant:<8} same-document fragment links on claims: {links}, unresolved: {unresolved}')
PY
