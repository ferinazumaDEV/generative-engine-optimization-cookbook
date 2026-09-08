# Schema — `meta.yml` and the dataset files

`schema_version: 2`

Every recipe in this cookbook carries a `meta.yml`. Before this schema existed the
files drifted: some had `metric`, `before_value` and `sample_size`, others had none
of them, and the vocabulary for `confidence` was inconsistent. This document fixes
one schema and applies it to all six recipes, so the recipes can be aggregated into
a single dataset without anybody guessing a missing value.

**The rule that matters: a field with no real measured value is `null`, never an
estimate.** `null` means "this recipe does not report that number"; `0` means "the
measurement ran and the answer was zero". They are different things and the dataset
keeps them apart — in the CSV a `null` is an empty cell.

## `meta.yml`

The file is deliberately **flat**: scalars and single-line lists only, no nested
mappings. That keeps it readable by `grep`, by a human, and by the ~30-line
standard-library parser in [`build.sh`](build.sh) — the cookbook has no third-party
dependencies and this schema does not add one. All six files carry the same keys in
the same order.

| Key | Type | Meaning |
|---|---|---|
| `schema_version` | integer | Version of this schema. Currently `1`. |
| `technique` | string | Stable identifier; matches the recipe's directory name. |
| `title` | string | Human title of the recipe. |
| `chapter` | string | Cookbook chapter directory, e.g. `04-technical`. |
| `handbook_section` | string | The handbook chapter this recipe demonstrates. |
| `status` | string | `published` once the recipe carries a real measurement. |
| `method` | string | How the number was obtained. All six are `deterministic-offline`. |
| `evidence_class` | string | **What this number already finishes.** One of `technical-seo`, `aeo`, `geo-precondition`. See below. |
| `evidence_note` | string | One sentence saying *why* it is in that class. Required; the class without the reason is an assertion. |
| `requires_llm` | boolean | Whether reproducing the measurement needs a model. |
| `requires_network` | boolean | Whether reproducing the measurement needs the network. |
| `tool` | string | What actually computes the number. |
| `engines` | list | Answer-engine crawlers the recipe is written about. Context, not a measured population. |
| `metric` | string | The **primary** measured quantity, in words. |
| `unit` | string | Unit of `before_value` / `after_value`. |
| `before_value` | number | Primary metric on the `before/` variant. |
| `after_value` | number | Primary metric on the `after/` variant. |
| `secondary_metric` | string \| null | A second quantity the same run reports, or `null`. |
| `secondary_unit` | string \| null | Unit of the secondary values. |
| `secondary_before_value` | number \| null | Secondary metric on `before/`. |
| `secondary_after_value` | number \| null | Secondary metric on `after/`. |
| `secondary_role` | string \| null | `secondary` (a second effect) or `denominator` (the base the primary metric is counted out of). |
| `sample_size` | number \| null | The N the recipe's `measurement.md` states, or `null` when it states none. |
| `sample_unit` | string \| null | What that N counts — the unit is *not* comparable across recipes. |
| `confidence` | string \| null | `low`, `low-moderate`, `moderate` or `null`. Copied from the recipe's `measurement.md`. |
| `measured_date` | date | The date printed in the recipe's `measurement.md`. |
| `last_verified` | date | The last date `reproduce.sh` was re-run and its output still matched. |
| `limitations` | string | One sentence naming the proxy and stating that it is not a citation measurement. |

### Notes on specific values

- **`sample_size` is not uniform, on purpose.** Each recipe counts a different unit
  (one article; two artefacts; eight user-agents; five entities; eight claims), so
  `sample_unit` always travels with it. Do not sum or average these across recipes.
- **`ssr-vs-csr-rendering` has `sample_size`, `sample_unit` and `confidence` set to
  `null`** because its `measurement.md` states none of the three. That gap is left
  visible rather than filled in.
- **`confidence` vocabulary.** Three of the recipes word it as "moderate", one as
  "low–moderate", and `ai-crawler-access` words it "Medium" in prose; the schema
  records that last one as `moderate` (same rung, one vocabulary). No confidence
  level was raised or lowered.
- **`engines` is context, not data.** It lists the crawlers the technique is written
  about. Only `ai-crawler-access` actually measures anything per user-agent.

## `reproduce.sh --json`

Every recipe's `reproduce.sh` accepts `--json`. Without the flag the output is the
same human-readable table it always printed; with it, the script prints one JSON
object on stdout and nothing else. Both paths are offline, deterministic and exit 0.

```
{
  "technique", "chapter", "handbook_section", "title",   identifying fields
  "method", "requires_llm", "requires_network",          how it was measured
  "measurements": [                                      one entry per number
    { "id", "role", "metric", "unit", "before_value", "after_value" }
  ],
  "table": [ ... ]                                       the rows of the text table
}
```

`role` is `primary`, `secondary` or `denominator`, exactly as in `meta.yml`.
`table` carries the same per-variant rows the text output shows, so nothing that is
visible to a human reader is lost in the machine-readable path.

## The dataset files

[`build.sh`](build.sh) runs the six recipes with `--json` and cross-checks every
field against that recipe's `meta.yml`. **If a measured value and its front-matter
disagree, the build fails and writes nothing** — so a number can never reach the
dataset without a script that produced it.

`geo-offline-measurements.json` holds the metadata, one `recipes[]` entry per recipe
(including the per-variant rows) and a flat `measurements[]` array. The metadata
carries `version`, `doi` and `date_modified`, read by `build.sh` from the
`version`, `doi` and `date-released` lines of [`CITATION.cff`](../CITATION.cff)
(which are bumped together with every git tag), and `author`, so the JSON can be
cited and dated on its own; they must agree with `about.jsonld`. The CSV is that
same flat array, one row per measurement:

| Column | Notes |
|---|---|
| `technique`, `chapter`, `recipe_path`, `handbook_section`, `title` | Which recipe the row comes from. |
| `metric_id`, `metric_role`, `metric`, `unit` | Which number the row is. |
| `before_value`, `after_value` | Measured. |
| `absolute_change`, `ratio_after_over_before` | **Derived** by `build.sh` from the two measured values. The ratio is empty when `before_value` is 0, because a ratio to zero is undefined — not infinite. |
| `method`, `requires_llm`, `requires_network`, `engines`, `tool` | How it was measured. `engines` is `;`-separated. |
| `sample_size`, `sample_unit`, `confidence` | As above; empty when the recipe reports none. |
| `measured_date`, `last_verified` | Dates. |
| `limitations` | The one-sentence proxy caveat for that recipe. |

An empty cell always means "no value reported", never zero.


## `evidence_class` — what the number already finishes

Added in `schema_version: 2`. It is **not** a confidence rating, and it does not
grade how well anything was measured: every value in this dataset is measured
directly and deterministically, and nothing is estimated.

What it separates is whether the property measured **is the deliverable**, or only a
step toward an outcome nobody has observed.

| Value | Meaning | Example |
|---|---|---|
| `technical-seo` | The measured property is itself the outcome of technical SEO. A reader can reproduce it with `curl` and the job is done. | A fetch-only crawler reads *n* words of the page. That is not a stand-in for readability — it **is** readability. |
| `aeo` | Same, for answer surfaces: the measured property is what an answer engine consumes. | A schema.org parser extracts *n* typed facts. Answer boxes consume parsed facts directly. |
| `geo-precondition` | Measured just as directly, but one step short of the outcome. It shows the artifact is *ready* to be retrieved, resolved or cited — not that it is. | Chunks come out self-contained from a fixed-size splitter. A real retriever's chunking is unknown, so this is readiness, not retrieval. |

**Why this distinction exists.** Before it, all six recipes carried the same caveat —
"an offline proxy" — and that undersold three of them. Being readable by a fetch-only
crawler, being parseable by schema.org, and admitting a named crawler in `robots.txt`
are complete outcomes in their own disciplines; calling them proxies for citation
buries evidence that is already finished.

**What it does NOT license.** No row, in any class, measures retrieval, reranking,
generation or citation by an answer engine. `technical-seo` and `aeo` mean the number
finishes *its own* discipline, never that it demonstrates a generative engine cites
anything. That claim is not made anywhere in this dataset and would need a different
kind of study.

**Closed vocabulary, enforced twice.** `build.sh` refuses to write a dataset whose
`evidence_class` is outside the three values, and `validate.py` refuses to pass the
published artifacts if one slipped through. Overclaiming here would look exactly like
a typo, which is why a typo cannot get in.
