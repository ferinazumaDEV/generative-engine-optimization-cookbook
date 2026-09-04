# Changelog

All notable changes to **The GEO Cookbook** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Because
this is a collection of measured experiments rather than a library, a "version" is a
state of the corpus: which recipes exist, what they measure, and with which numbers.

Every figure in a release is reproducible offline from the tag it belongs to.

## [Unreleased]

## [0.1.0] — 2026-09-04

First tagged state of the corpus: six reproducible recipes and the dataset that
aggregates their measurements.

### Added

- **`dataset/`** — the six measurements published together as a citable dataset:
  `geo-offline-measurements.csv` and `.json`, a documented `SCHEMA.md`, and
  `build.sh`, which regenerates both files by running every recipe. Figures in the
  dataset are produced by the recipes themselves, not transcribed by hand.
- **`--json` output on all six `reproduce.sh`** scripts, so each measurement can be
  consumed by a machine. Without the flag the scripts behave exactly as before.
- **A common front-matter schema across the six `meta.yml`** files: metric, unit,
  before and after values, method, sample size, dates and an explicit limitations
  field. Fields with no real value are left absent rather than filled in.
- Six recipes, each with a `before/` artifact, an `after/` artifact, measurement
  notes stating the method and its limits, and a one-command reproduction script:
  `ssr-vs-csr-rendering`, `structured-data-jsonld`, `ai-crawler-access`,
  `chunk-friendly-structure`, `entity-clarity-sameas`, `citation-anchoring`.
- **"What is measured, and what is not"** table in the README: for every recipe, the
  offline property it measures, and `not measured` in the retrieval, reranking,
  generation and citation columns.
- `llms.txt` listing all six recipes, a `How to cite` section, and licences GitHub
  can detect: CC BY 4.0 for the prose, MIT for the code under `LICENSES/`.

### Scope of the claims

Every measurement in this repository is **deterministic, offline, and reproducible**:
no network, no API key, no language model. Each one shows that an intervention changes
a specific machine-readable property of a controlled artifact.

**None of them shows that an answer engine cites a page more often.** Repeated
identical queries against live engines overlap at a Jaccard index of roughly 0.32–0.43
on the cited sources within a single day ([arXiv:2604.07585](https://arxiv.org/abs/2604.07585)),
so a lift measured with few runs sits inside the noise. That link — from a measured
property to an actual citation — is an open research question, and this repository
does not claim it.

[Unreleased]: https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook/releases/tag/v0.1.0
