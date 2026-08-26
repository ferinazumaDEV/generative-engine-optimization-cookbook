#!/usr/bin/env bash
# What does an AI crawler that does NOT execute JavaScript actually see?
# This extracts the visible text from each page's HTML SOURCE (scripts, styles
# and tags stripped) and counts the words. No network, no browser, no LLM.
set -euo pipefail
cd "$(dirname "$0")"

extract() {
  perl -0777 -pe 's/<script.*?<\/script>//gis; s/<style.*?<\/style>//gis; s/<!--.*?-->//gis; s/<[^>]+>/ /g; s/&[a-z]+;/ /g; s/\s+/ /g; s/^\s+|\s+$//g' "$1"
}

printf '%-8s %-22s %s\n' "VARIANT" "RENDERING" "WORDS A NO-JS CRAWLER READS"
for variant in before after; do
  label=$([ "$variant" = before ] && echo "client-side (CSR)" || echo "server-side (SSR/SSG)")
  words=$(extract "$variant/index.html" | wc -w | tr -d ' ')
  printf '%-8s %-22s %s\n' "$variant" "$label" "$words"
done

echo
echo "Both pages look identical to a human in a browser."
echo "To a fetch-only AI crawler, only the SSR (after) version has readable content."
