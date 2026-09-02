# Entity clarity — disambiguate with `sameAs` + canonical IDs

**A bare name is not an entity.** When your page says "Apple", "Python" or "Michael Jordan", a machine building an answer has to *guess* which one you mean — the company or the fruit, the language or the snake, the athlete or the AI professor. Guess wrong and it attaches your claims to the wrong thing. Pinning each name to a **canonical ID** (a Wikidata item, mirrored with `sameAs` links to Wikidata/Wikipedia) removes the guess: the name now resolves to exactly one real-world thing.

> In this example, the "before" page declares **5** named entities and **0** of them resolve to a canonical ID; the "after" page — same article, same names — resolves **5 of 5**. Deterministic, dated and reproducible below.

## The technique in 30 seconds

- **Problem:** structured data (or prose) that names entities with `"name": "Apple"` and nothing else. The name is ambiguous; a machine cannot look it up.
- **Fix:** give each entity a canonical `@id` (a Wikidata Q-ID) and a `sameAs` array pointing at Wikidata and Wikipedia. One name → one canonical identity.
- **Check yours:** run `reproduce.sh` — it counts how many of your declared entities pin to exactly one Wikidata ID. Bare names score 0.

## Hypothesis

Adding `sameAs` links to canonical knowledge-base IDs (Wikidata/Wikipedia) makes the entities on a page **unambiguously resolvable by a machine**, where the same entities named in plain text are not.

- **Independent variable:** the presence of canonical `@id` + `sameAs` links on each entity in the page's JSON-LD.
- **Control (`before/`):** the article's JSON-LD lists 5 entities by `name` only — no IDs, no `sameAs`.
- **Treatment (`after/`):** the **same article** and the **same 5 names**, each entity now carrying a Wikidata `@id` and a `sameAs` array (Wikidata + Wikipedia).
- **Dependent variable (measured):** number of entities that resolve to exactly one canonical Wikidata ID.

## Before / after

| Variant | Structured data | Entities resolved to a canonical ID |
|---|---|---|
| [`before/`](before/) | names only | **0** / 5 |
| [`after/`](after/) | names + `sameAs` (Wikidata) | **5** / 5 |

Both pages show the **same article** to a human. Run it yourself:

```bash
bash reproduce.sh
```

No network, no browser, no LLM — it parses the JSON-LD from each page's HTML source and counts, per entity, the distinct canonical Wikidata IDs it declares.

## How it was measured

See [`measurement.md`](measurement.md). In short: parse the JSON-LD `about` list, and for each entity count the distinct Wikidata Q-IDs reachable via `@id` and `sameAs`. An entity is "resolved" when that count is exactly one. Method, numbers, N and date are in the file.

## What this proves — and what it doesn't

This measures **machine-resolvability of entities**, nothing more.

> **5/5 resolvable ≠ 5× more likely to be cited.**

Resolvability is a *precondition* for an engine attaching your claims to the right real-world thing — not a citation multiplier. Whether an engine actually cites you, and whether it picks the *correct* Wikidata item, depends on the engine and on the IDs being right. This recipe proves the entities become **unambiguously anchored**; it does not claim a citation rate. A causal "cited more" claim needs a separate **live-LLM** test.

## FAQ

**Why Wikidata and not just Wikipedia?**
A Wikidata Q-ID is a stable, language-independent identifier for the *thing*; Wikipedia URLs are human-readable mirrors of it. Providing both in `sameAs` gives machines the canonical anchor and a corroborating source.

**Isn't this just schema.org markup / SEO?**
The markup overlaps with classic structured data, but the goal is different: in GEO the entity must resolve to **one** real-world thing an engine can ground an answer on, not merely be tagged.

**Do I have to hand-write Q-IDs?**
For a handful of key entities, yes — look them up on wikidata.org. It is a one-time cost per entity and it is exactly the ambiguity a machine cannot resolve on its own.

---
<!-- ecosystem:start -->
Part of the **[GEO Cookbook](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook)** — reproducible examples for **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. Theory: **[Chapter 04 — Technical GEO](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook/blob/main/docs/04-technical.md)**. Hub: **[zentimes.es](https://zentimes.es)**. By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
