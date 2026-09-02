# Measurement — entity disambiguation with `sameAs`

**Question:** of the named entities a page declares, how many resolve **unambiguously** to a single canonical real-world thing that a machine can look up?

**Method:** parse the JSON-LD from each page. For every entity in the article's `about` list, collect the distinct **canonical Wikidata Q-IDs** it declares through `@id` and `sameAs`. An entity counts as *unambiguously resolved* when that set has **exactly one** member:

- **0 IDs** → a bare name (e.g. "Apple") that a machine cannot pin to one thing.
- **1 ID** → the name is anchored to exactly one Wikidata item.
- **>1 distinct IDs** → conflicting anchors; deliberately **not** counted as resolved.

Both variants contain the **same article** and the **same five entity names** (`Michael Jordan`, `Apple`, `Python`, `Amazon`, `Paris`) — each genuinely ambiguous when written as a bare name. Only the structured data differs.

**Command:** `bash reproduce.sh` (deterministic, offline — no network, no browser, no LLM). The check is pure string/JSON parsing over the page source with the Python 3 standard library.

## Results

| Variant | Structured data | Entities | Resolved to a canonical ID |
|---|---|---|---|
| `before/index.html` | names only, no IDs | 5 | **0** |
| `after/index.html` | names + `sameAs` (Wikidata + Wikipedia) | 5 | **5** |

- **Before → after:** `0 → 5` of 5 entities become unambiguously resolvable (0% → 100% of the entities on the page).
- **Sample size (N):** 5 entities, one page per variant.
- **Tool:** Python 3.11 standard library (`json`, `re`, `pathlib`) via `reproduce.sh`.
- **Date:** 2026-09-01. Re-run `reproduce.sh` to reproduce.

## What this does and does not show

- **Does show:** the *mechanical resolvability* of each named entity to one canonical identifier — a necessary condition for an engine to attach the page's claims to the **right** real-world thing instead of guessing.
- **Does NOT show:** that any given LLM or answer engine will therefore cite the page more often, or resolve the entity correctly downstream. This measures **machine-extractability / readability as a proxy**; it isolates one link in the chain. Proving a citation or accuracy lift requires a separate **live-LLM measurement** (prompt real engines, compare grounding/citation with and without the `sameAs` block), which this offline recipe intentionally does not attempt.
- **Caveat on the IDs:** the script validates the **form and uniqueness** of each canonical link (one Wikidata Q-ID per entity), not that the Q-ID is the semantically correct item — an offline check cannot dereference Wikidata. The IDs used here (`Q41421`, `Q312`, `Q28865`, `Q3884`, `Q90`) were chosen as the intended real items, but the *number* this experiment reports is the count of unambiguous anchors, not a correctness audit.

**Confidence:** moderate for the proxy claim (the count is exact, deterministic and reproducible); **low** for any leap to "cited more" without live-LLM evidence.
