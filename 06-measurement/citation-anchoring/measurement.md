# Measurement — citation anchoring

**Question:** how many of a document's claims carry an inline, linkable source *right next to the claim*, so that an extractor can lift the assertion and its backing URL as one unit?

**Method:** parse each variant's document **source**. Inside the marked claims block (`<!-- claims:start --> … <!-- claims:end -->`), each markdown list item is one **claim**. A claim counts as a **claim→source pair** when the same line contains at least one inline linkable source — a markdown link with an `http(s)` URL, i.e. `[text](https://…)` adjacent to the claim. Count the pairs. Both variants contain the **same eight claims**, in the same order, with identical wording; the only difference is whether each claim carries its source inline.

**Tool:** `reproduce.sh` — bash wrapper around a `python3` standard-library parser (`re`). Deterministic and offline: no network, no browser, no LLM, no randomness.

**Command:** `bash reproduce.sh`

## Results

| Variant | Document | Claims | Claim→source pairs a parser extracts |
|---|---|---|---|
| `before/article.md` | unsourced | 8 | **0** |
| `after/article.md` | citation-anchored | 8 | **8** |

- **Sample size (N):** 8 claims per document (identical set in both variants).
- **before → after:** 0 → 8 extractable claim→source pairs (0% → 100% of the claims anchored).
- The eight claims in `before/` are stated as fact with **no linkable path** back to any authority; a parser extracts zero (claim, source) pairs. In `after/` every claim ends with an inline citation, so all eight extract cleanly as (claim, source) pairs.
- **Date:** 2026-09-01. Re-run `reproduce.sh` to reproduce.

## Integrity check — fragment targets

`reproduce.sh` also reports `unresolved_fragment_links`: links on claim lines that point at a fragment of **this same document** (`[text](#id)`) whose target is missing or declared more than once. It is not part of the pair count and does not change it; it exists because a pipeline that resolves relative links against the page URL turns a broken `#id` into an `https://` link the pair count would score as a source. Run it on the links as written.

| Variant | Same-document fragment links on claims | Unresolved |
|---|---|---|
| `before/article.md` | 0 | **0** |
| `after/article.md` | 0 | **0** |

Neither fixture links into itself, so on this recipe the check certifies the 8 pairs rather than moving them. Its definitions and controls are in [`INSTRUMENTS.md`](../../INSTRUMENTS.md) §6.

## Confidence

**Low–moderate.** The count itself is exact and fully reproducible (deterministic parser over fixed input). The *interpretation* — that more extractable claim→source pairs makes an engine more likely to cite the page — is **not** tested here. See Limitations.

## Limitations

- **This measures machine-extractability / readability as a PROXY, not citation.** The number is "how many claim→source pairs a deterministic parser can lift from the document," which is a structural precondition for an engine to attribute a claim to a source — not proof that any LLM or answer engine actually cites more often. A live-LLM evaluation (prompting real engines and measuring attribution/citation rate) is a **separate experiment** and is not performed here.
- **It does not check that the sources are correct or authoritative.** The parser verifies that a linkable source is present and adjacent to the claim; it does not fetch the URL, confirm it resolves, or judge whether it actually supports the claim. (The sample sources in `after/` point to canonical specs and vendor docs — MDN, the RFC Editor, sitemaps.org, schema.org, Google Search Central — but the metric would score any syntactically valid inline link the same way.)
- **Operationalization is deliberate, not the only choice.** "Claim" is operationalized as a list item inside the marked block, and "source" as an inline `http(s)` markdown link on the same line. Footnote-style or reference-style citations would need the parser extended; prose paragraphs would need a sentence splitter. The definition was fixed *before* measuring and applied identically to both variants.
- **Small, controlled sample.** N = 8 hand-written claims in one document. This isolates the technique; it is not a survey of real-world pages.
