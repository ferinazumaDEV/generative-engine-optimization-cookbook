# Chunk-friendly structure — write pages a retriever can slice cleanly

**Answer engines do not read your page whole. They split it into fixed-size chunks and embed each one on its own.** A chunk that begins in the middle of a sentence and ends in the middle of another is a bad retrieval unit: out of context it is ambiguous, so it is retrieved and quoted less cleanly. The fix is not more words — it is *structure*. Headings, short sections and lists give the splitter natural seams to cut on, so every chunk lands as a complete, self-contained idea.

> In this example the exact same prose, poured into one wall of text, yields **0 of 5** self-contained chunks. Restructured with headings and lists it yields **5 of 5 (100%)** — *same sentences*, cut on clean seams. Measured, dated and reproducible below.

## The technique in 30 seconds

- **Problem:** one long undivided block has no seams. A fixed-size chunker is forced to cut it at an arbitrary character, straight through a sentence. Every interior chunk starts and ends mid-thought.
- **Fix:** break the same content into headings + short sections + lists. Now the chunker cuts *between* units, and each chunk is a whole heading, a whole sentence, or a whole list item.
- **Check yours:** run any document through a fixed-size splitter and eyeball the chunk boundaries — if chunks routinely start with a lowercase word, your structure is fighting the retriever.

## Hypothesis

Given the **same prose** and the **same fixed-size chunker**, a chunk-friendly structure (headings, short sections, lists) produces more **self-contained chunks** — chunks that begin at a unit boundary and end at one — than an undivided wall of text.

## Experiment design

- **Independent variable:** document *structure* only (wall of text vs. headings/sections/lists).
- **Control:** [`before/article.md`](before/article.md) — the article as a single undivided block of prose.
- **Treatment:** [`after/article.md`](after/article.md) — the **same sentences**, reorganised under headings with short sections and bullet lists.
- **Held constant:** the prose itself, the chunker, `chunk_size = 800`, zero overlap, and the separator order (`["\n\n", "\n", " ", ""]` — the standard recursive-splitter default).

## Before / after

| Variant | Structure | Self-contained chunks |
|---|---|---|
| [`before/`](before/) | wall of text | **0 / 5 (0%)** |
| [`after/`](after/) | chunk-friendly | **5 / 5 (100%)** |

Run it yourself:

```bash
bash reproduce.sh
```

No network, no browser, no LLM, no randomness — it splits each file with a deterministic recursive fixed-size chunker and counts how many chunks stand on their own.

## How it was measured

See [`measurement.md`](measurement.md). In short: chunk each file at 800 characters with the standard recursive splitter, then count the chunks that **start** at a unit boundary (heading, list item, or a new sentence) **and end** at one (terminal punctuation or a heading line). Method, numbers and date are in the file.

## What this shows — and what it doesn't

This measures **retrieval-unit cleanliness**: how well your content survives being chopped into fixed-size chunks. It is a machine-extractability proxy, nothing more.

> **100% self-contained chunks ≠ 100% more citations.**

Clean chunks are a *precondition* for good retrieval, not a guarantee of it. Whether a chunk is actually retrieved and cited still depends on relevance, authority, embedding quality and the engine. This recipe proves the content becomes **cleanly chunkable**; it does not, on its own, prove an LLM cites it more — that needs a separate live-LLM measurement.

## FAQ

**Isn't 800 characters arbitrary?**
It is one common chunk size. The *effect* — walls of text get cut mid-sentence, structured text cuts on seams — holds across sizes; change `CHUNK_SIZE` in `reproduce.sh` and re-run to see it move together.

**Do I have to write in bullet points everywhere?**
No. The lever is *seams*: headings and paragraph breaks at natural idea boundaries. Lists help, but a wall of text broken into short, well-titled paragraphs already chunks cleanly.

**Isn't this just good writing?**
It overlaps with it, but the stakes differ: here the unit of consumption is a chunk an engine reads without its neighbours, so each section has to make sense alone.

---
<!-- ecosystem:start -->
Part of the **[GEO Cookbook](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook)** — reproducible examples for **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. Theory: **[Chapter 03 — Content](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook/blob/main/docs/03-content.md)**. Hub: **[zentimes.es](https://zentimes.es)**. By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
