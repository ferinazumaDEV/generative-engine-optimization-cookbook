# Measurement — JSON-LD structured data extractability

**Question:** how many typed facts can a schema.org / JSON-LD parser extract from
the page — the machine-readable statements an AI engine can lift without guessing
from prose?

**Method:** for each variant, take the **HTML source** the server returns, pull
out every `<script type="application/ld+json">` block, parse it as JSON, and walk
the tree counting:

- **Typed entities** — JSON objects that carry an `@type` (a `Recipe`, `Person`,
  `Organization`, `Question`, `HowToStep`, …).
- **Typed facts** — property assertions made *about* those typed entities: every
  key on a typed object other than `@context` / `@type` (e.g. `Recipe.prepTime`,
  `Person.name`, `Answer.text`). One key = one asserted fact.

Both variants render the **same visible article** to a human. The only difference
is that `after/` includes a JSON-LD block; `before/` does not.

**Command:** `bash reproduce.sh` (deterministic, offline — no network, no browser,
no LLM, no randomness; pure `python3` stdlib).

## Results

| Variant | JSON-LD present | Typed entities | Typed facts extracted |
|---|---|---|---|
| `before/index.html` | no | 0 | **0** |
| `after/index.html` | yes | 17 | **37** |

- **Sample size (N):** 2 artefacts (one page, two variants) — this is a single
  controlled A/B pair, not a corpus study.
- **Before:** the article's content exists only as prose and HTML tags. A
  JSON-LD/schema.org parser extracts **0** typed facts — the author, the times,
  the ingredients, the Q&A are all there for a human but carry no machine type.
- **After:** the same article plus one JSON-LD `@graph` yields **17** typed
  entities and **37** typed facts (an absolute gain — the ratio is undefined
  because the baseline is 0).
- **Tool:** `python3` 3.11 stdlib (`re` + `json`), via `reproduce.sh`.
- **Date:** 2026-09-01. Re-run `reproduce.sh` to reproduce.

## Limitations

**Confidence: moderate — as a proxy for extractability, not for citation.**

- **This measures a PROXY.** The number is the count of typed facts a JSON-LD
  parser can read — i.e. the **machine-readability / extractability** of the
  page's content. It is a *mechanical* property of the HTML, measured exactly and
  reproducibly.
- **It does NOT prove an LLM cites you more.** A higher typed-fact count is a
  *necessary-ish enabler* — structured, typed data is easier for an engine to
  parse, attribute and quote — but this experiment does **not** establish, on its
  own, a causal increase in citation rate, ranking, or answer inclusion. That
  requires a separate **live-LLM measurement** (prompt real engines, compare
  citation/answer behaviour with and without the markup, across many pages).
- **Counting choices are conventions.** "Typed entity" = object with `@type`;
  "typed fact" = one non-`@type`/`@context` key on such an object. Different but
  reasonable counting rules (e.g. counting each array element, or nested-object
  properties differently) would shift the absolute numbers. The **direction**
  (0 → many) is robust to those choices; the exact 37 is convention-dependent.
- **Validity ≠ correctness of content.** The script checks that typed facts are
  *present and parseable*, not that they are *true* or that they match the visible
  text. Mismatched or spammy JSON-LD can be penalised by engines; keep the markup
  faithful to the page.
- **N is tiny.** One page, one topic. Treat the numbers as an existence proof of
  the mechanism, not an effect-size estimate.
