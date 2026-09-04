# GEO offline measurements — dataset

Six deterministic, offline before/after measurements of **machine legibility**, one
per recipe of this cookbook, published as data instead of only as prose.

- [`geo-offline-measurements.csv`](geo-offline-measurements.csv) — one row per measurement (11 rows).
- [`geo-offline-measurements.json`](geo-offline-measurements.json) — the same rows plus per-variant detail and metadata.
- [`SCHEMA.md`](SCHEMA.md) — what every field means, including which ones are measured and which are derived.
- [`build.sh`](build.sh) — regenerates both files from the recipes.

## What this is *not*

Read this before using the numbers.

**These are proxies for machine legibility. They do not measure citation.** Every
value answers a mechanical question about a file — how many words survive tag
stripping, how many typed facts a JSON-LD parser reads, how many chunks come out of
a splitter intact, how many user-agents a `robots.txt` admits, how many names carry
one canonical ID, how many claims carry an inline link. None of them observes an
answer engine. Nothing here shows that ChatGPT, Claude, Perplexity, Google's AI
Overviews or any other engine retrieves, ranks, quotes or **cites** the `after`
variant more often than the `before` one. That question is not measured, not
estimated and not claimed anywhere in this dataset.

Three more limits worth stating plainly:

- **The samples are tiny and controlled**, by design. Each row comes from one
  artifact in two variants — one article, one page, one `robots.txt` pair. These are
  mechanism demonstrations, not effect-size estimates, and they support no
  extrapolation to a population of real websites.
- **Several metrics have a zero baseline** (0 → 37 typed facts, 0 → 8 pairs). The
  jump is real and reproducible, but a ratio against zero is undefined, so the CSV
  leaves `ratio_after_over_before` empty rather than printing an impressive number.
  Only `ssr-vs-csr-rendering` has a non-trivial ratio (6 → 152 words, 25.33×).
- **The counting rules are conventions.** "Self-contained chunk", "typed fact",
  "claim→source pair" and "unambiguously resolved entity" are each operationalised
  in the recipe's `measurement.md`. Reasonable alternative definitions would shift
  the absolute numbers; the direction of each effect is what is robust. Every
  recipe's own `measurement.md` carries its full method, caveats and confidence, and
  each row repeats a one-sentence `limitations` field.

## What each row measures

| Recipe | Metric (role) | before → after | Unit |
|---|---|---|---|
| [`chunk-friendly-structure`](../03-content/chunk-friendly-structure/) | chunks that come out self-contained from a fixed-size splitter (primary) | 0 → 5 | chunks |
| [`chunk-friendly-structure`](../03-content/chunk-friendly-structure/) | chunks the splitter produces (denominator) | 5 → 5 | chunks |
| [`ssr-vs-csr-rendering`](../04-technical/ssr-vs-csr-rendering/) | words a crawler that does not execute JavaScript can read (primary) | 6 → 152 | words |
| [`structured-data-jsonld`](../04-technical/structured-data-jsonld/) | typed facts a JSON-LD parser extracts (primary) | 0 → 37 | typed facts |
| [`structured-data-jsonld`](../04-technical/structured-data-jsonld/) | typed entities a JSON-LD parser extracts (secondary) | 0 → 17 | typed entities |
| [`ai-crawler-access`](../04-technical/ai-crawler-access/) | AI crawler user-agents allowed by `robots.txt` for `/` (primary) | 0 → 8 | user-agents |
| [`ai-crawler-access`](../04-technical/ai-crawler-access/) | bytes of curated content exposed by `llms.txt` (secondary) | 0 → 2868 | bytes |
| [`entity-clarity-sameas`](../05-authority/entity-clarity-sameas/) | names resolved to exactly one canonical Wikidata Q-ID (primary) | 0 → 5 | entities |
| [`entity-clarity-sameas`](../05-authority/entity-clarity-sameas/) | names the page declares (denominator) | 5 → 5 | entities |
| [`citation-anchoring`](../06-measurement/citation-anchoring/) | claim→source pairs a parser extracts (primary) | 0 → 8 | claim-source pairs |
| [`citation-anchoring`](../06-measurement/citation-anchoring/) | claims in the marked block (denominator) | 8 → 8 | claims |

A **denominator** row is the base its primary is counted out of, not a second
effect: 0 of 5 chunks became 5 of 5, and 0 of 8 claims became 8 of 8.

## How to regenerate it

```bash
bash dataset/build.sh
```

That is the whole procedure. It runs each recipe's `reproduce.sh --json`, checks
every value against that recipe's `meta.yml`, and rewrites the CSV and the JSON.

- **No network, no browser, no model, no third-party packages** — bash and the
  Python 3 standard library only, the same as every recipe.
- **Deterministic.** There are no timestamps in the output, so rebuilding an
  unchanged tree produces byte-identical files and a stale dataset shows up as a
  `git diff`.
- **It fails loudly.** If a recipe's measured output disagrees with its front-matter,
  the build stops and writes nothing rather than publishing a number no script
  produced. Never edit the CSV or the JSON by hand; change the recipe and rebuild.

## Provenance

Each row is produced by the `reproduce.sh` of the recipe named in `recipe_path`, and
the same numbers are published, with their full method and caveats, in that recipe's
`measurement.md`. `measured_date` is the date in that `measurement.md`;
`last_verified` is the last date the script was re-run and still produced the same
output.

## License

Same terms as the rest of the cookbook: the data files and this prose are
**CC BY 4.0** ([`LICENSE`](../LICENSE), [canonical text](https://creativecommons.org/licenses/by/4.0/));
`build.sh` and the recipe scripts are **MIT** ([`LICENSES/MIT.txt`](../LICENSES/MIT.txt)).
Reuse the numbers freely, credit the source, and keep the "what this is not" section
attached to them.

## How to cite

Citation metadata for the repository lives in [`CITATION.cff`](../CITATION.cff).
Plain text:

```
Aporta Franco, Fernando (2026). The GEO Cookbook — GEO offline measurements dataset.
https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook (hub: https://zentimes.es)
```
