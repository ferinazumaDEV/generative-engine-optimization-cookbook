# Measurement — AI crawler access

**Question:** is an answer engine (a) *permitted* to fetch this site, and (b) handed a curated, machine-readable feed to extract from?

**Method:** two deterministic, offline proxies measured over each variant's files.

1. **AI user-agents allowed by robots.txt.** A stdlib-Python parser groups the
   robots.txt rules by user-agent. For each of 8 canonical AI crawlers it selects
   the applicable group (exact user-agent match, else the `*` group), then
   resolves the rule for path `/`: the longest matching path wins, and `Allow`
   breaks ties with `Disallow`; an empty `Disallow:` means "allow all". It counts
   how many of the 8 come out allowed.
2. **Curated bytes exposed by llms.txt.** The byte size of `llms.txt`
   (`os.path.getsize`), or `0` when the file is absent.

Both variants describe the **same site**; only the crawler policy differs.

**Canonical AI user-agents tested (N = 8):** GPTBot, ClaudeBot, anthropic-ai,
PerplexityBot, Google-Extended, CCBot, Applebot-Extended, Bytespider.

**Command:** `bash reproduce.sh` (deterministic, offline — no network, no
browser, no LLM). **Tool:** `python3` standard library + Bash only.

## Results

| Variant | robots.txt policy | llms.txt | AI UAs allowed (of 8) | Curated bytes |
|---|---|---|---|---|
| `before/` | blocks AI crawlers | absent | **0** | **0** |
| `after/`  | allows AI crawlers | present | **8** | **2868** |

- **Access:** 0 → 8 AI crawlers permitted (0% → 100% of the tested set).
- **Curated content exposed:** 0 → 2868 bytes.
- **Date:** 2026-09-01. Re-run `reproduce.sh` to reproduce.
- These are the exact figures printed by `reproduce.sh` on this machine; they
  are not rounded or estimated.

## Confidence

**Medium.** The two numbers are fully deterministic and re-derivable from the
files, so the *measurement* is high-confidence. Confidence is capped at medium
because the numbers are **proxies for access/extractability**, not a measured
citation outcome (see Limitations). The robots.txt evaluator implements the
common convention (most-specific group, longest-match, Allow-wins) but is a
simplified model, not a byte-for-byte reimplementation of every engine's parser.

## Limitations

- **This measures a precondition, not an effect.** "8 crawlers allowed + 2868
  curated bytes" says the site is *reachable and has an extractable feed*. It
  does **not** prove that any LLM or answer engine will cite it, or cite it more.
  Access is a gate; citation depends on relevance, authority and each engine's
  ranking, none of which is measured here.
- **No live-LLM measurement.** Proving a causal lift in citations requires a
  separate study: ask real answer engines a battery of questions before/after,
  with a control site, and count citations — that is out of scope here (needs
  network + LLMs and is non-deterministic) and is deliberately not claimed.
- **llms.txt is an emerging convention.** Publishing it and having it obeyed are
  different things; crawler support for [llmstxt.org](https://llmstxt.org) is
  uneven and changing. Bytes exposed is a proxy for "curated content made
  available", not proof of consumption.
- **robots.txt is honor-system + simplified here.** Compliance is voluntary per
  crawler, user-agent lists change over time, and this parser models path `/`
  only with the standard precedence rules — real engines differ in edge cases.
- **Sample size.** One before/after site pair; N = 8 user-agents for the access
  proxy. The point is the mechanism, not a population estimate.
