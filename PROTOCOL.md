# Protocol — does machine legibility change citation by generative engines?

**Status: preregistered design, not yet run.** Version 1.0, 2026-09-13. No data
has been collected under this protocol. Nothing in this repository claims an
effect on any engine; this document says how such a claim *could* be earned,
and commits to the design before any result exists so the result cannot shape
it. It is not registered externally yet; the section *Registration* says what
that would take and why it matters.

Everything else in this cookbook measures **preconditions** — whether a page's
content is visible to a crawler that does not run JavaScript, whether its facts
are typed, whether its entities resolve. Those are offline, deterministic and
reproducible, and they say nothing about what an engine does with the page.
This protocol is the bridge between the two, and it is deliberately narrow.

## 1. Question

> For a page that exists in two variants identical in substance and different
> only in machine legibility — the `before/` and `after/` of a cookbook recipe —
> does the `after/` variant get cited by generative answer engines more often
> than the `before/` variant, for the same queries, over the same window?

One question. It is not "does GEO work"; it is whether one specific, offline-
measurable change moves one specific, observable outcome.

## 2. Hypotheses (fixed before any data)

- **H1.** Over the query panel and window, the `after/` variant is cited in a
  higher fraction of answers than the `before/` variant.
- **H0.** No difference, or a difference within the noise floor measured in
  section 7.

A result that fails to reject H0 is a result. It is reported the same way.

## 3. What is measured, per observation

One observation is one query, sent once, to one engine, on one date, from one
documented location and session state. For each, record:

| Field | Values |
|---|---|
| `variant_cited` | `before` / `after` / `both` / `neither` |
| `cited_urls` | every URL the answer attributes, verbatim |
| `position` | rank of our domain among cited sources, or `—` |
| `abstained` | the engine gave no answer or no sources (`true`/`false`) |
| `answer_hash` | SHA-256 of the answer text, for change detection |
| `screenshot` | file name |

The outcome is `variant_cited`. Everything else is context that lets a reader
audit the outcome or explain a surprise.

## 4. Treatment and control

Each recipe already ships a controlled pair: `before/` and `after/` differ in
exactly the property the recipe measures and in nothing else. Both variants are
hosted at stable, distinct URLs on the same domain, published on the same day,
with the same title, the same author and the same canonical-free status, so
that neither is preferred by anything other than the property under test.

Publishing the pair is a prerequisite, not part of the protocol, and it is
recorded: URL of each variant, date published, and the commit of this
repository they were built from.

## 5. Query panel (frozen before publication)

Twelve queries per recipe, written and committed **before** the pair is
published, in `protocol/queries/<recipe>.txt`. Half are questions the page
answers directly; half are adjacent questions where the page is one plausible
source among many. Queries are never edited after the panel is frozen; a query
that turns out to be malformed is dropped with a note, not replaced.

The panel is the unit of pre-registration: a study whose queries were chosen
after seeing which ones cite the page has measured its own selection.

## 6. Engines, conditions, window

- **Engines:** ChatGPT (with search), Perplexity, Google AI Overviews / AI
  Mode, Gemini, Copilot. An engine that cannot be observed under the stated
  conditions is reported as *not observed*, never inferred.
- **Conditions:** private session, no account, one named country, one named
  language, desktop web. All four are recorded per observation; any change
  starts a new series.
- **Window:** four dates, one per week, starting no earlier than 14 days after
  the pair is published (engines need to have crawled it — and *whether* they
  did is checked, section 8). Each query is sent once per engine per date.

That is 12 queries × 5 engines × 4 dates = **240 observations per recipe**, and
the study covers as many recipes as have a publishable pair — at least three.

## 7. Noise floor, measured first

Before comparing variants, the same panel is run twice on the same date, one
hour apart, against the *same* variant. The disagreement between the two runs
is the noise floor. A between-variant difference smaller than the noise floor
is reported as *within noise*, whatever its sign. This follows the design
argument in Schulte, Bleeker & Kaufmann (2026), *Don't Measure Once*
([arXiv:2604.07585](https://arxiv.org/abs/2604.07585)): a single observation of
an AI search result is not a measurement of a distribution.

## 8. What is checked before the data is believed

- **Crawl evidence.** Server logs for each variant's URL: which engine user-
  agents fetched it, when. A variant no engine has fetched cannot be cited, and
  a "no citation" for it is not evidence about legibility.
- **Reachability.** Both variants return 200, are not blocked in `robots.txt`
  for the engines under test, and render the same text with JavaScript off.
- **Panel integrity.** The committed query file's hash matches what was sent.

## 9. Analysis, decided now

Per recipe and per engine: the fraction of observations in which each variant
is cited, with a 95% interval (Wilson). The comparison is the difference of
fractions with its interval. Then the same pooled across engines, reported
*alongside* the per-engine figures, never instead of them — engines differ, and
a pooled number hides that.

There is no threshold for "success". The report states the difference, the
interval, the noise floor and the crawl evidence, and lets the reader judge.

**Exploratory analysis** — anything not in this section — is labelled as such
and kept in a separate part of the report.

## 10. What is published

The raw observation table (all fields of section 3, screenshots included), the
frozen query panel with its hash, the crawl-log extracts, the noise-floor runs,
and the analysis script. If any of those cannot be published, the report says
which and why, and the result is downgraded to *not independently checkable*.

## 11. What this protocol does not claim

- It does not measure ranking, traffic or business outcomes.
- It does not generalise beyond the recipes, engines, country, language and
  window stated. A result on three pages in one country in one month is a
  result on three pages in one country in one month.
- It does not make the offline measurements in this cookbook mean more than
  they do. They remain preconditions; this protocol tests whether one of them
  predicts an outcome, once.

## 12. Registration

This document being in git with a date is not preregistration; a commit can be
rewritten. Preregistration means a third party holds a timestamped copy that
the authors cannot alter. The intended route is a Zenodo deposit of this file
(or an OSF registration) **before the query panel is published**, with the DOI
recorded here. Until that line carries a DOI, the honest word for this document
is *design*, not *preregistration*.

> Registered: *not yet*. DOI: —.

## 13. Relationship to the earlier observation protocol

A separate, earlier note (4 September 2026) describes a one-pass observation of
citation *formatting* in minor engines, to replace two secondary-sourced
sentences in the handbook. That is a product-behaviour check: one pass, no
control, no repetition, and it says so. It is not a study and this protocol
does not subsume it. The two answer different questions and should not be
confused: that one asks *how* an engine cites; this one asks *whether* a change
we made alters *what* it cites.

## 14. Sources

- Aggarwal et al., *GEO: Generative Engine Optimization*, KDD 2024 —
  [arXiv:2311.09735](https://arxiv.org/abs/2311.09735). The controlled design
  this protocol borrows from, on a benchmark rather than live engines.
- Schulte, Bleeker & Kaufmann, *Don't Measure Once: Measuring Visibility in AI
  Search (GEO)*, 2026 — [arXiv:2604.07585](https://arxiv.org/abs/2604.07585).
  Why one observation is not a measurement.
- Wilson, E. B. (1927), *Probable inference, the law of succession, and
  statistical inference*, JASA 22(158) —
  [doi:10.1080/01621459.1927.10502953](https://doi.org/10.1080/01621459.1927.10502953).
  The interval used in section 9.
