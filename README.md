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
  meta.yml         machine-readable front-matter (see dataset/SCHEMA.md)
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

## What is measured, and what is not

| Recipe | Measured property (offline proxy) | Retrieval | Reranking | Generation | Citation |
|---|---|---|---|---|---|
| [`ssr-vs-csr-rendering`](04-technical/ssr-vs-csr-rendering/) | Words visible to a crawler that does not execute JavaScript: 6 → 152 (~25.3×) | not measured | not measured | not measured | not measured |
| [`structured-data-jsonld`](04-technical/structured-data-jsonld/) | Typed entities and typed facts a JSON-LD parser extracts: 0 → 17 entities, 0 → 37 facts | not measured | not measured | not measured | not measured |
| [`ai-crawler-access`](04-technical/ai-crawler-access/) | AI user-agents allowed by `robots.txt`: 0 → 8 of 8; bytes of `llms.txt` exposed: 0 → 2,868 | not measured | not measured | not measured | not measured |
| [`chunk-friendly-structure`](03-content/chunk-friendly-structure/) | Chunks that come out self-contained from a fixed-size splitter (`chunk_size = 800`): 0 of 5 → 5 of 5 | not measured | not measured | not measured | not measured |
| [`entity-clarity-sameas`](05-authority/entity-clarity-sameas/) | Named entities resolved to exactly one canonical Wikidata ID: 0 → 5 of 5 | not measured | not measured | not measured | not measured |
| [`citation-anchoring`](06-measurement/citation-anchoring/) | Claims carrying an inline, linkable source (claim→source pairs a parser extracts): 0 → 8 of 8 | not measured | not measured | not measured | not measured |

Each recipe measures a machine-legibility property of a controlled artifact — one page or one document in two variants, checked offline by a deterministic script. None of them claims an effect on retrieval, reranking, generation or citation by any engine; those four columns are the open research questions this cookbook does not answer. The proxy, sample size, confidence and limitations of each number are stated in the recipe's own `measurement.md`.

The same numbers are also published as data in [`dataset/`](dataset/) — a CSV and a JSON file with one row per measurement, plus the units, sample sizes, confidence and limitations of each. They are generated from the recipes themselves with `bash dataset/build.sh`, which re-runs every `reproduce.sh --json` and refuses to write anything if a measured value disagrees with its recipe's front-matter. Read [`dataset/README.md`](dataset/README.md) before reusing them: it states what the rows do *not* show.

## Start here

New to this? Read the **[handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)** first for the *why*, then come here to *do it*. Open [`04-technical/ssr-vs-csr-rendering`](04-technical/ssr-vs-csr-rendering/) and run `bash reproduce.sh`.

## Contributing

New cited technique or a fix? Each example must carry a real, reproducible measurement (or be explicit about what isn't measurable). No invented numbers.

## How to cite

Citation metadata lives in [`CITATION.cff`](CITATION.cff); GitHub renders it as the **"Cite this repository"** button in the sidebar (see [about citation files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)). Plain text:

```
Aporta Franco, Fernando (2026). The GEO Cookbook. https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook (hub: https://zentimes.es)
```

## License

Copyright (C) 2026 Fernando Aporta Franco. Code samples are **MIT** — see [`LICENSES/MIT.txt`](LICENSES/MIT.txt). Prose (README / measurement notes) is **CC BY 4.0** — see [`LICENSE`](LICENSE). In short: copy the code freely, credit the words.

---
<!-- ecosystem:start -->
Part of the **ferinazumaDEV** GEO ecosystem:

- **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)** — the open reference (theory).
- **The GEO Cookbook** — reproducible examples (practice, this repo).
- Hub & writing: **[zentimes.es](https://zentimes.es)**

By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
