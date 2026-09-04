#!/usr/bin/env bash
# What does an AI crawler that does NOT execute JavaScript actually see?
# This extracts the visible text from each page's HTML SOURCE (scripts, styles
# and tags stripped) and counts the words. No network, no browser, no LLM.
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

extract() {
  perl -0777 -pe 's/<script.*?<\/script>//gis; s/<style.*?<\/style>//gis; s/<!--.*?-->//gis; s/<[^>]+>/ /g; s/&[a-z]+;/ /g; s/\s+/ /g; s/^\s+|\s+$//g' "$1"
}

before_label="client-side (CSR)"
after_label="server-side (SSR/SSG)"
before_words=$(extract "before/index.html" | wc -w | tr -d ' ')
after_words=$(extract "after/index.html" | wc -w | tr -d ' ')

if [ "$JSON" -eq 1 ]; then
  cat <<JSON
{
  "technique": "ssr-vs-csr-rendering",
  "chapter": "04-technical",
  "handbook_section": "docs/04-technical.md",
  "title": "SSR vs CSR: make your content visible to AI crawlers",
  "method": "deterministic-offline",
  "requires_llm": false,
  "requires_network": false,
  "measurements": [
    {
      "id": "words_visible_no_js",
      "role": "primary",
      "metric": "words of the HTML source a crawler that does not execute JavaScript can read",
      "unit": "words",
      "before_value": ${before_words},
      "after_value": ${after_words}
    }
  ],
  "table": [
    {
      "variant": "before",
      "rendering": "${before_label}",
      "words_visible_no_js": ${before_words}
    },
    {
      "variant": "after",
      "rendering": "${after_label}",
      "words_visible_no_js": ${after_words}
    }
  ]
}
JSON
  exit 0
fi

printf '%-8s %-22s %s\n' "VARIANT" "RENDERING" "WORDS A NO-JS CRAWLER READS"
printf '%-8s %-22s %s\n' "before" "$before_label" "$before_words"
printf '%-8s %-22s %s\n' "after" "$after_label" "$after_words"

echo
echo "Both pages look identical to a human in a browser."
echo "To a fetch-only AI crawler, only the SSR (after) version has readable content."
