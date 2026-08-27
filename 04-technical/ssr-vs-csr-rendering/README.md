# SSR vs CSR — make your content visible to AI crawlers

**If your page renders its main content with client-side JavaScript, most AI crawlers will not see it.** Bots like GPTBot, ClaudeBot and PerplexityBot fetch your HTML but do not reliably execute JavaScript. A client-side-rendered (CSR) page looks empty to them — and empty pages do not get cited. Server-side rendering (SSR) or static generation (SSG) puts the content in the HTML itself, where every crawler can read and quote it.

> In this example, the CSR page exposes **6 words** to a no-JS crawler; the SSR page exposes **152** — the *same article*, about **25× more visible**. Measured, dated and reproducible below.

## The technique in 30 seconds

- **Problem:** `<div id="root"></div>` + a JS bundle → the article only exists *after* a browser runs JavaScript. A fetch-only crawler sees an empty shell.
- **Fix:** render (or pre-render) the content into the HTML the server sends. The crawler reads the article without running anything.
- **Check yours:** `curl -s https://your-page | your-text-extractor` — if your main content is not in that output, an AI crawler probably cannot see it either.

## Before / after

| Variant | Rendering | Words a no-JS crawler reads |
|---|---|---|
| [`before/`](before/) | client-side (CSR) | **6** |
| [`after/`](after/) | server-side (SSR/SSG) | **152** |

Both pages show the **same article** to a human in a browser. Run it yourself:

```bash
bash reproduce.sh
```

No network, no browser, no LLM — it just extracts the text a fetch-only bot would get from each page's HTML source and counts the words.

## How it was measured

See [`measurement.md`](measurement.md). In short: strip `<script>`/`<style>`/tags from each page's **HTML source** (that is what a crawler which does not execute JavaScript receives) and count the visible words. Method, numbers and date are in the file.

## What 25× means — and what it doesn't

This measures **HTML text a fetch-only crawler can read**, nothing more.

> **25× more visible words ≠ 25× more likely to be cited.**

Visibility is a *precondition* for citation — an empty page cannot be quoted — not a multiplier on it. Whether a visible passage is actually cited depends on relevance, authority, and the engine. This recipe proves the content becomes **extractable**; it does not claim a citation rate.

## FAQ

**Do AI crawlers really not run JavaScript?**
Most fetch HTML and parse it without a full browser render; rendering, where it happens at all, is slower and rate-limited. Making your main content depend on client-side JS is a bet you do not need to make. *(Engine behavior shifts — see the handbook chapter for current, sourced detail.)*

**Isn't this just SEO?**
The mechanism overlaps with classic crawlability, but the stakes differ: in GEO the page must be *extractable into an answer*, not merely indexed. Invisible content cannot be quoted.

**I use React / Vue / Angular — do I have to drop them?**
No. Use their SSR/SSG modes (Next.js, Nuxt, Astro, SvelteKit…) so the first HTML response already contains the content.

---
<!-- ecosystem:start -->
Part of the **[GEO Cookbook](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook)** — reproducible examples for **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. Theory: **[Chapter 04 — Technical GEO](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook/blob/main/docs/04-technical.md)**. Hub: **[zentimes.es](https://zentimes.es)**. By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
