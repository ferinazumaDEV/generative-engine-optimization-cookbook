# Claims — what each recipe measures, and what it does not

This file states, per recipe, which claim is measured, which is not, and how to read the grade. `about.jsonld` (`additionalProperty` → `maturity`, `reproducible`) is the source of truth for the work-level statement; `meta.yml` in each recipe is the source of truth for the numbers. When this file disagrees with either, this file is wrong.

## Vocabulary

| Grade | Meaning | Test |
|---|---|---|
| `established` | Reproducible effect, primary source, stated scope. | Someone else gets the same result from the primary source or from a script in this cluster. |
| `mixed` | Evidence points both ways; the scope decides. | At least one primary source for and one against, or a clear effect in one setting and none in another. |
| `experimental` | Plausible from mechanism, one study, or an uncontrolled observation; not measured under control. | No controlled measurement of the effect exists. **Default grade for any technique whose effect on citation has not been measured.** |
| `folklore` | Widely repeated; no reproducible evidence, or debunked. | The search for a primary source ends at other people repeating it. |
| `reproducible` (`yes` / `no`) | Orthogonal flag: a script in this cluster re-derives the number offline. | Here: `bash reproduce.sh` in the recipe directory. |

**Alias: `solid` == `established`** — the spelling the evidence ledger in [prompt-engineering-evidence](https://github.com/ferinazumaDEV/prompt-engineering-evidence) uses. Same meaning.

## How the recipe metadata maps onto the vocabulary

| Field | Where | Meaning for the grade |
|---|---|---|
| `method: deterministic-offline`, `requires_llm: false`, `requires_network: false` | `meta.yml` | `reproducible: yes` — `bash reproduce.sh` re-derives the numbers with no network and no model |
| `status: published` | `meta.yml` ([SCHEMA.md](dataset/SCHEMA.md)) | the recipe carries a real measurement; it is not a maturity grade |
| `last_verified` | `meta.yml` | the last date the script's output still matched the front matter |
| `confidence` (`low`, `low-moderate`, `moderate`) | `meta.yml`, copied from `measurement.md` | how well the proxy captures the property — not confidence in an engine effect |
| `limitations` | `meta.yml` | the one sentence every number travels with |
| Retrieval / Reranking / Generation / Citation = `not measured` | README, "What is measured, and what is not" | the engine effect is `experimental` for every recipe |

## Source versus primary source

- The **primary source** for every number is the recipe's own `reproduce.sh` — and [`dataset/build.sh`](dataset/build.sh), which refuses to write a value the script did not produce.
- The handbook chapter named in `handbook_section` is a **source** for *why* the technique should matter — the rationale — not primary evidence that any engine cites the `after/` variant more often.
- The primary source for why a small live test cannot settle the engine effect is [arXiv:2604.07585](https://arxiv.org/abs/2604.07585): repeated identical queries cite different sources within a day, so a lift measured with few runs sits inside the noise.

## Per-technique format, mapped onto a recipe directory

**Definition** = the recipe README's opening statement · **Answer** = its "Fix" · **Evidence** = `measurement.md` + `meta.yml` · **Implementation** = `after/` · **Limitations** = the `limitations` field · **Sources** = `reproduce.sh` (primary) and `handbook_section` (source).

## The six recipes, graded

| Recipe | Measured property (before → after) | Property | Engine effect | Reproducible | Confidence | Limitation (from `meta.yml`) |
|---|---|---|---|---|---|---|
| [`ssr-vs-csr-rendering`](04-technical/ssr-vs-csr-rendering/) | words a no-JS crawler reads: 6 → 152 | `established` | `experimental` | yes | not stated | Measures the mechanical visibility of the text to a fetch-only crawler, not whether any answer engine cites the page. |
| [`structured-data-jsonld`](04-technical/structured-data-jsonld/) | typed facts a JSON-LD parser extracts: 0 → 37 (entities 0 → 17) | `established` | `experimental` | yes | moderate | Measures the extractability of typed statements from the page source, not whether any answer engine cites the page. |
| [`ai-crawler-access`](04-technical/ai-crawler-access/) | AI user-agents allowed for `/`: 0 → 8 of 8 (llms.txt bytes 0 → 2,868) | `established` | `experimental` | yes | moderate | Measures a precondition (reachability and an extractable feed), not whether any answer engine cites the page. |
| [`chunk-friendly-structure`](03-content/chunk-friendly-structure/) | self-contained chunks from a fixed-size splitter: 0 of 5 → 5 of 5 | `established` | `experimental` | yes | moderate | Measures a machine-legibility proxy (whether a chunk stands alone after fixed-size splitting), not whether any answer engine cites the page. |
| [`entity-clarity-sameas`](05-authority/entity-clarity-sameas/) | entities resolved to one Wikidata Q-ID: 0 → 5 of 5 | `established` | `experimental` | yes | moderate | Measures the mechanical resolvability of each name to one canonical identifier, not whether any answer engine cites the page. |
| [`citation-anchoring`](06-measurement/citation-anchoring/) | claim→source pairs a parser lifts: 0 → 8 of 8 | `established` | `experimental` | yes | low-moderate | Measures how many claim-to-source pairs a parser can lift from the document, not whether any answer engine cites the page. |

"Property `established`" means the deterministic measurement holds for the controlled artifact and anyone can re-run it; each recipe is one page or one document in two variants (`sample_size` 1–8, unit stated per recipe, not comparable across recipes). "Engine effect `experimental`" means no recipe measures retrieval, reranking, generation or citation by any engine; that link is the open question this cookbook does not answer.

## Work-level maturity

`about.jsonld` does not yet carry `additionalProperty`; the values proposed for the owner to set there are `maturity: experimental` and `reproducible: yes`: everything here re-runs offline, and none of it shows an engine citing a page more often.

## Changing a grade

A recipe's engine-effect grade moves from `experimental` only with a measurement of an engine — dated, named model, N and seed stated, the noise floor from arXiv:2604.07585 acknowledged — in a PR. The same PR bumps `dateModified` in `about.jsonld`; the README ID card, `llms.txt` and `dataset/` follow it.
