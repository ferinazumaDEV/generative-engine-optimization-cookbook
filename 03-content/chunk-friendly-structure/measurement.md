# Measurement — chunk-friendly structure vs. wall of text

**Question:** given the same prose and the same fixed-size chunker, how many chunks come out *self-contained* — usable on their own by a retriever — depending only on how the document is structured?

**Method:** each variant is split with a standard **recursive character text splitter** (`chunk_size = 800`, no overlap, separator order `["\n\n", "\n", " ", ""]` — the [LangChain RecursiveCharacterTextSplitter default](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)). This is the realistic default a RAG pipeline uses: it prefers to break on paragraph, then line, then word boundaries, and only hard-cuts when a single block exceeds the size. Each resulting chunk is then classified **self-contained** if BOTH hold:

- **starts clean** — the first non-whitespace character begins a unit: a heading (`#`), a list marker (`-`, `*`, `>`), a digit, or an uppercase letter (a new sentence). A mid-sentence hard cut starts with a lowercase continuation word and fails this.
- **ends clean** — the chunk ends with terminal punctuation (`.`, `!`, `?`, `:`) or its last line is a heading. A chunk cut mid-sentence ends on a bare word and fails this.

Both files contain the **same sentences**; only `after/` adds headings, short sections and bullet lists. The classification is purely textual and deterministic — no network, no browser, no LLM, no randomness.

**Command:** `bash reproduce.sh`

## Results

| Variant | Structure | Chunks | Self-contained | Share |
|---|---|---|---|---|
| `before/article.md` | wall of text | 5 | 0 | 0.0% |
| `after/article.md` | chunk-friendly | 5 | 5 | 100.0% |

- Both variants split into the **same number of chunks (5)** — the comparison is like-for-like, isolating structure.
- **Wall of text:** 0 of 5 chunks stand alone. The article is one undivided block, so the 800-char splitter cuts it on word boundaries straight through sentences; interior chunks start on a lowercase word and end on a bare word.
- **Chunk-friendly:** 5 of 5 chunks stand alone. The splitter breaks between headings, sections and list items, so each chunk is a whole heading + section or a set of complete sentences/list items.
- **Sample:** N = 1 article (~530 words), rendered in two structures. Small by design — this isolates one variable cleanly; it is a mechanism demo, not a corpus study.
- **Tool:** `reproduce.sh`, Python 3 standard library only (no third-party deps).
- **Date:** 2026-09-01. Re-run `reproduce.sh` to reproduce.

## Confidence

**Moderate, and scoped.** The direction of the effect is robust — an undivided block *must* be hard-cut by any fixed-size chunker, while structured text offers seams to cut on — and the script is deterministic, so the numbers reproduce exactly. But the magnitude (0% vs 100%) is specific to this article, this chunk size, and this definition of "self-contained"; treat it as an illustration of the mechanism, not a universal constant.

## Limitations

- **This is an extractability / machine-legibility PROXY, not a citation measurement.** It shows that structured content survives fixed-size chunking as clean, self-contained units — a *precondition* for good retrieval. By itself it does **not** prove causally that any LLM or answer engine cites the structured version more. Establishing that requires a separate **live-LLM measurement** (feed both variants to real engines and compare retrieval/citation), which this experiment deliberately does not attempt.
- **"Self-contained" is a heuristic.** The start/end rules approximate "does this chunk begin and end a thought" with punctuation and casing. They can misclassify edge cases (e.g. a sentence that legitimately starts with a lowercase token, or a heading with no trailing punctuation is handled specially but other formats may not be). The measure is a proxy for readability of a chunk in isolation, not a semantic judgement of completeness.
- **Single sample, single chunk size.** N = 1 article at `chunk_size = 800`. The effect direction holds across sizes (change `CHUNK_SIZE` and re-run), but the exact shares will shift with content length and chunker settings.
- **Real chunkers vary.** Production pipelines add chunk overlap, semantic/markdown-aware splitting, or token-based sizing, any of which softens the penalty a wall of text pays here. The recursive character splitter used is a common, but not universal, default.
