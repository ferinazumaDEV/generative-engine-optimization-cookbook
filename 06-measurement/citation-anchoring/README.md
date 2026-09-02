# Citation anchoring — put a linkable source next to every claim

**A claim with no source is a dead end for a machine.** When your document asserts a fact but leaves no linkable path to the authority behind it, an answer engine that wants to attribute the statement has nothing to point at — the (claim, source) pair it would lift simply is not there. **Citation anchoring** fixes this by attaching an inline, linkable source *right next to* each claim, so the assertion and its backing URL travel together as one extractable unit.

> In this example, the **same eight claims** are written twice. The unsourced version exposes **0** claim→source pairs a parser can extract; the anchored version exposes **8** — every claim anchored. Measured, dated and reproducible below.

## The technique in 30 seconds

- **Problem:** "robots.txt was standardized as RFC 9309 in 2022." — true, but a machine reading it has no adjacent link to attribute it to. To an extractor, that is an unbacked assertion.
- **Fix:** anchor the claim inline — `…standardized as RFC 9309 in 2022 ([RFC 9309](https://www.rfc-editor.org/rfc/rfc9309)).` Now the claim and its source are one adjacent, extractable pair.
- **Check yours:** run `reproduce.sh` (or `grep`) over your document — count the claims, then count how many carry a linkable source on the same line. The gap is your unanchored surface.

## Hypothesis

Anchoring each claim to an inline linkable source increases the number of **claim→source pairs** a deterministic parser can extract from the document — the structural precondition an answer engine needs to attribute a statement to a source.

- **Independent variable:** whether each claim carries an inline linkable source (`[text](https://…)`) adjacent to it.
- **Control (`before/`):** eight claims stated as fact, no sources.
- **Treatment (`after/`):** the **same eight claims**, same wording and order, each ending in an inline citation.
- **Held constant:** the claim set, their wording, their order, the document structure, and the parser.

## Before / after

| Variant | Document | Claim→source pairs a parser extracts |
|---|---|---|
| [`before/`](before/) | unsourced | **0** |
| [`after/`](after/) | citation-anchored | **8** |

Both documents state the same eight facts. Run it yourself:

```bash
bash reproduce.sh
```

No network, no browser, no LLM — it parses each document's source, counts the claims, and counts how many have a linkable source adjacent to the claim.

## How it was measured

See [`measurement.md`](measurement.md). In short: inside a marked claims block, each list item is one claim; a claim scores as a **claim→source pair** when the same line contains an inline `http(s)` markdown link. Method, numbers, N and date are in the file.

## What 0 → 8 means — and what it doesn't

This measures **claim→source pairs a deterministic parser can extract**, nothing more.

> **8 extractable pairs ≠ 8 citations by an engine.**

Extractability is a *precondition* for attribution — an engine cannot point at a source that is not there — not a guarantee of it. Whether a visible, anchored claim is actually cited depends on relevance, authority and the engine. This recipe proves the (claim, source) pairs become **extractable**; it does not claim a citation rate. A live-LLM test is a separate experiment — see [`measurement.md`](measurement.md) → Limitations.

## FAQ

**Isn't a link at the bottom of the page enough?**
For a human, often. For an extractor, adjacency matters: a claim and its source on the same line pair unambiguously, while a bare list of links at the foot of the page leaves *which claim each supports* to guesswork.

**Do the sources have to be inline links specifically?**
The metric here rewards inline `http(s)` links because they are the most machine-unambiguous form. Footnote or reference-style citations can carry the same information; the parser would need a small extension to resolve them (noted in `measurement.md`).

**Does this check my sources are any good?**
No. It checks that a linkable source is *present and adjacent* to each claim. Correctness and authority of the source are your responsibility — anchoring a claim to a bad link still scores, and still misleads.

---
<!-- ecosystem:start -->
Part of the **[GEO Cookbook](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook)** — reproducible examples for **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. Hub: **[zentimes.es](https://zentimes.es)**. By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
