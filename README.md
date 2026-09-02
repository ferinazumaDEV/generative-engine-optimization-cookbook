# The GEO Cookbook

**Reproducible, measured examples of the techniques that get your content cited by AI answer engines** — the hands-on companion to **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. The handbook is the *theory* (what to do and why, with sources); this cookbook is the *practice*: for each technique, a `before/` and an `after/`, a one-command way to reproduce it, and the numbers it moves.

Every example is designed to be **run and verified by you** — most need no network, no browser and no LLM. Where a claim can only be measured, we measure it and date it; where it can't be, we say so.

## How each example is built

```
<chapter>/<technique>/
  README.md        answer-first: the technique, before/after, and the numbers
  before/          the un-optimized artifact
  after/           the optimized artifact
  measurement.md   method + numbers + date
  reproduce.sh     one command to re-run the demo and the measurement
  meta.yml         machine-readable front-matter (technique, chapter, engines, date)
```

## Techniques

Folders mirror the handbook's chapters. Theory-only chapters (foundations, engines overview, ethics, glossary) live in the handbook; the cookbook covers what can be *demonstrated*.

| Chapter | Technique | Status |
|---|---|---|
| 04 · Technical | [`ssr-vs-csr-rendering`](04-technical/ssr-vs-csr-rendering/) — is your content visible to a no-JS crawler? | ✅ **published** (25× demo) |
| 04 · Technical | [`structured-data-jsonld`](04-technical/structured-data-jsonld/) — make your facts machine-readable | ✅ **published** (0 → 37 typed facts) |
| 04 · Technical | [`ai-crawler-access`](04-technical/ai-crawler-access/) — allow AI crawlers in `robots.txt` and publish an `llms.txt` | ✅ **published** (0 → 8 UAs, 0 → 2,868 bytes) |
| 03 · Content | [`chunk-friendly-structure`](03-content/chunk-friendly-structure/) — write extractable, quotable sections | ✅ **published** (0/5 → 5/5 self-contained chunks) |
| 05 · Authority | [`entity-clarity-sameas`](05-authority/entity-clarity-sameas/) — `sameAs` / canonical Wikidata IDs | ✅ **published** (0 → 5 entities resolved) |
| 06 · Measurement | [`citation-anchoring`](06-measurement/citation-anchoring/) — a linkable source next to every claim | ✅ **published** (0 → 8 claim→source pairs) |

## Start here

New to this? Read the **[handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)** first for the *why*, then come here to *do it*. Open [`04-technical/ssr-vs-csr-rendering`](04-technical/ssr-vs-csr-rendering/) and run `bash reproduce.sh`.

## Contributing

New cited technique or a fix? Each example must carry a real, reproducible measurement (or be explicit about what isn't measurable). No invented numbers.

## License

Code samples are **MIT**; prose (README / measurement notes) is **CC BY 4.0**. See [`LICENSE`](LICENSE). In short: copy the code freely, credit the words.

---
<!-- ecosystem:start -->
Part of the **ferinazumaDEV** GEO ecosystem:

- **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)** — the open reference (theory).
- **The GEO Cookbook** — reproducible examples (practice, this repo).
- Hub & writing: **[zentimes.es](https://zentimes.es)**

By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
