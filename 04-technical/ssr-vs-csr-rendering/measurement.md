# Measurement — SSR vs CSR visibility

**Question:** how much of a page's content can an AI crawler that does *not* execute JavaScript actually read?

**Method:** for each variant, take the **HTML source** the server would return (the exact bytes a fetch-only crawler receives), remove `<script>` and `<style>` blocks and all tags, and count the remaining words. This approximates the text available to a crawler that fetches HTML but does not run a browser. Both variants render the **same article** for a human.

**Command:** `bash reproduce.sh` (deterministic, offline — no network, browser or LLM).

## Results

| Variant | Rendering | Words visible to a no-JS crawler |
|---|---|---|
| `before/index.html` | client-side (CSR) | 6 |
| `after/index.html` | server-side (SSR/SSG) | 152 |

- **Ratio:** ~**25.3×** more visible content in the SSR version.
- The 6 words the CSR page exposes are just the `<title>` — the article body (the citable content) is **entirely** invisible to a fetch-only crawler.
- **Date:** 2026-08-26. Re-run `reproduce.sh` to reproduce.

## What this does and does not show

- **Does show:** the *mechanical visibility* of your content to a crawler that does not execute JavaScript — a necessary condition for being quoted.
- **Does not show:** whether a given engine ultimately cites you (that depends on authority, relevance and the engine's ranking). This example isolates one link in the chain: if the content is not in the HTML, nothing downstream can happen.
- **Caveat:** some crawlers render some JavaScript some of the time, and this behavior changes. Treat "does not execute JS" as the safe assumption, not a universal law — see the handbook chapter for current, sourced engine behavior.
