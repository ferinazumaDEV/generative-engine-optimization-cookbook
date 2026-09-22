# Changelog

All notable changes to **The GEO Cookbook** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Because
this is a collection of measured experiments rather than a library, a "version" is a
state of the corpus: which recipes exist, what they measure, and with which numbers.

Every figure in a release is reproducible offline from the tag it belongs to.

> Version headings are plain text on purpose: a changelog that links its own tag
> cannot pass a link check before that tag exists. Compare views are one click away
> from the [releases page](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook/releases).
>
> The README's version row follows the same rule, and for the same reason: it links
> the releases page rather than `releases/tag/vX.Y.Z`. Linking the exact tag makes
> every release a chicken-and-egg — the link check fails on the pull request because
> the tag is created after the merge. It failed exactly that way on v0.1.2 before the
> row was changed.

## [Unreleased]

### Fixed

- `protocol/probes/engine-answering-control.py` told a refusal apart from a wrong
  answer only in `network-is-clean.py`, not in itself: a rate-limited `HTTP 202`
  from DuckDuckGo was reported as "the engine returned pages that do not answer
  the control queries", which is not what happened — no pages came back at all.
  Each control now reports **answered**, **wrong-query** or **declined**. Both
  failures still void the run and still exit non-zero, so nothing that gates on
  the exit status changes; what changes is that the recorded reason is true.
  The distinction is the whole substance of section 13-ter, so a probe shipped
  with that addendum could not be blurring it.
- Verified with all three outcomes observed live in one test on 2026-09-22: Bing
  answered one control and returned voting information for the other, while
  DuckDuckGo declined both with `HTTP 202`.

### Added

- `PROTOCOL.md` section 13-ter, a dated addendum: the one engine 13-bis found
  observable was, four hours later, returning result pages that answer a
  different query — right title, no CAPTCHA, ten well-formed results, a
  different unrelated set on each request, and at 15:47:08Z one control query
  passing while another failed in the same run. The preregistration is not
  edited; the addendum records what was measured and what it changes.
- `protocol/probes/`: the two checks that afternoon forced into existence.
  `engine-answering-control.py` asserts that a control query returns a named
  domain its correct answer must contain, over at least two queries, and exits
  non-zero so a run can be gated on it. `network-is-clean.py` decides whether
  the machine's own view of the web is intact before an engine is blamed, and
  reports a corroborating engine as *corroborates*, *contradicts* or
  *inconclusive* so that its silence cannot be read as an alarm. Standard
  library only: no browser, no account, no API key.

### Changed

- The rule a run is gated on is now positive: a control asserts a correct
  answer rather than the absence of a refusal, and any one control failing
  voids the entire run. A void run is discarded, not recorded as zeros.

## [0.1.3] — 2026-09-13

### Added

- `PROTOCOL.md`: a preregistered design for the one question this cookbook has
  never answered — whether a machine-legibility change alters citation by
  generative engines. Controlled pairs (`before/`/`after/`), a query panel
  frozen before publication, five engines, four dates, a measured noise floor,
  crawl evidence before results are believed, and the analysis decided in
  advance. **Not yet run, and not yet externally registered**; the document
  says what would make it so, and until then calls itself a design.

### Fixed

- **`ai-crawler-access`: the robots.txt matcher now implements RFC 9309.** It
  compared patterns with `str.startswith`, so `*` and `$` were ordinary text and
  `Disallow: /*` — the most common way to block a site — scored as *8 of 8
  allowed*. `*` now matches any sequence, a trailing `$` anchors to the end of
  the path, the longest pattern wins and Allow breaks an equal-length tie.
  (External re-audit, F06.)
- **`entity-clarity-sameas`: only complete Wikidata entity URLs count.** The
  matcher used an unanchored `re.search`, so any string merely *containing*
  something Q-ID-shaped counted — including one not hosted on Wikidata at all.
  Scheme, host and path are now checked and the Q-ID must be the whole final
  segment. (External re-audit, F07.)
- **`structured-data-jsonld`: a commented-out block is not on the page, and a
  block that does not parse yields nothing instead of aborting the run.** The
  extractor scanned the raw HTML, so `<!-- <script type="application/ld+json">…
  -->` counted, and a single malformed block made `json.loads` raise and the
  whole measurement die. Comments are stripped first; unparseable blocks are
  skipped and the others still count. Found by the negative controls below.
- **`citation-anchoring`: code is quoted, not asserted, and an image is not a
  source.** A list item inside a fenced code block counted as a claim, a link
  inside an inline code span counted as its source, and `![alt](https://…)`
  counted as a linkable reference. Fenced blocks are skipped, code spans are
  ignored when looking for the link, and image embeds are excluded. Found by the
  negative controls below.
- **`ssr-vs-csr-rendering`: numeric character references are not words.** The
  stripper removed `&amp;`-style entities only, so `&#8212;` and `&#x2014;` each
  counted as a visible word. Found by the negative controls below.

### Changed

- **`ai-crawler-access`: the metric is renamed to say what it counts.** *AI
  crawler user-agents* → *AI-related robots.txt tokens*, because the eight
  tokens mix retrieval, training and usage-control tokens and two of them
  (`Google-Extended`, `Applebot-Extended`) have no HTTP user-agent. Each token
  now carries its role and the vendor's own documentation in `reproduce.sh`. The
  script's output no longer infers citability from access.
- The dataset's `limitations` note for that recipe explains the taxonomy and
  states that the values did not change.

### Added

- **`INSTRUMENTS.md`** — the specification of the six instruments: what each
  counts, what it deliberately does not, and how its definition has changed,
  with the rule that a definition change is made test-first and never moves a
  published value silently.
- `tests/test_instruments.py`: a conformance corpus for all six instruments,
  94 checks, mostly negative controls — inputs that look like the thing being
  counted and must not count. For robots.txt and Wikidata: wildcards, end
  anchors, Allow/Disallow ties, regex metacharacters that must stay literal,
  lookalike hosts, a property ID where an item ID is required. For the other
  four: malformed and commented-out JSON-LD, `@type` as a list, `@graph`,
  untyped values; scripts, styles, comments, attributes and entities that are
  not visible words (and `<noscript>`, which is exactly what a no-JS reader is
  served, pinned as counting); `javascript:` and relative links, bare URLs,
  reference-style links, code and images that are not sources; an empty
  document, a one-paragraph document and headings without bodies for the
  chunker. Plus one metamorphic check per instrument: reordering a document's
  units leaves the count alone, and concatenating it with itself doubles it.
  The four instruments that are Python heredocs or a bash function are
  executed straight out of their `reproduce.sh`, so the test cannot drift from
  the recipe. No network, no dependencies beyond python3, bash and perl.

**All 11 measured values are unchanged**, verified by rebuilding the dataset
and comparing record by record: the fixtures in this repository never contained
the inputs that defeated any of the five corrected instruments. `schema_version` stays at 2. Adding
`OAI-SearchBot` to the roster — which belongs there — would move 8 → 9 and is
deferred to a versioned dataset change (`0.2.0`, `schema_version: 3`) rather
than folded into a bug fix.

## [0.1.2] — 2026-09-06

The archived copy had fallen behind. `v0.1.1` was tagged on 4 September and seven
commits landed after it, including every piece of citation metadata — so the
Zenodo deposit people were citing did not contain the DOI, the maturity
declaration or the identity links it describes. This release closes that gap.

### Added

- **The dataset is now verified on every push and pull request.** The build is
  run, the result is diffed against what is committed, and it is run a second
  time to check it is deterministic. A new `dataset/validate.py` checks the
  published artifacts themselves: JSON structure against `SCHEMA.md`, the CSV
  carrying the same records field by field, derived columns recomputed from the
  measured values, citation scalars agreeing with `CITATION.cff`, and the
  "what this does not show" disclaimer still present. Until now CI checked that
  the links resolved but not that the measurements did.

- **DOI.** `v0.1.1` is archived on Zenodo, so the cookbook is now citable by a
  persistent identifier instead of a repository URL. The concept DOI
  [`10.5281/zenodo.22299279`](https://doi.org/10.5281/zenodo.22299279) always resolves to the latest release;
  each release also gets its own version DOI. Recorded in the README badge and
  citation, `CITATION.cff`, `about.jsonld` and `llms.txt`.

## [0.1.1] — 2026-09-04

Metadata only. No recipe, script, measurement or dataset row changed; `v0.1.0` and
`v0.1.1` contain byte-identical experiments.

### Fixed

- **`CITATION.cff` declared two licences as a YAML list.** That is valid CFF, but it
  converts to `{"id": ["MIT", "CC-BY-4.0"]}` in Zenodo's deposit format, which takes a
  single licence id. Zenodo rejected the deposit and archived the `v0.1.0` release as
  *Failed*, so no DOI was minted. The file now declares `CC-BY-4.0`, matching the root
  `LICENSE` and GitHub's own detection; the dual licence is unchanged and stated in
  [README](README.md#license) and `LICENSES/MIT.txt`. A comment in `CITATION.cff`
  records why the list must not come back.

### Added

- `abstract`, `keywords`, `version` and `date-released` in `CITATION.cff`, so the
  archived record carries a description and subject terms rather than a bare title.

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
