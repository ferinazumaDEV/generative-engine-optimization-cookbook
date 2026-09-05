# AI crawler access — let the answer engines in, then hand them a clean feed

**If your robots.txt blocks the AI crawlers, your site cannot be cited by an answer engine — full stop.** GPTBot, ClaudeBot, PerplexityBot, Google-Extended and friends identify themselves by user-agent (Google-Extended is the exception: per Google's crawler list it has no separate request user-agent string and works only as a robots.txt control token — https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers; Apple describes Applebot-Extended as a secondary user agent used to control data usage while Applebot does the crawling — https://support.apple.com/en-us/119829); a `Disallow: /` for those agents removes you from the pool of sources an engine is even allowed to fetch. The fix is two files: a robots.txt that *allows* those user-agents, and an `llms.txt` — a curated, plain-text index of your best content, written to be lifted straight into an answer.

> In this example the **before** site allows **0 of 8** known AI crawlers and publishes **0 bytes** of curated content; the **after** site allows **all 8** and exposes **2868 bytes** of clean, machine-readable content. Measured, dated and reproducible below.

## The technique in 30 seconds

- **Problem:** a blanket "block the AI bots" robots.txt (common since 2023) means answer engines are not permitted to fetch you at all — and there is no curated feed pointing them at your good content.
- **Fix:** (1) add `Allow: /` for each answer-engine user-agent in robots.txt; (2) publish `/llms.txt` (the [llmstxt.org](https://llmstxt.org) convention) — an H1 title, a blockquote summary, then sections of `[name](url): description` links to clean, self-contained pages.
- **Check yours:** fetch your robots.txt and confirm no `Disallow: /` applies to GPTBot/ClaudeBot/PerplexityBot/etc., then fetch `/llms.txt` and confirm it returns curated text, not a 404.

## Before / after

| Variant | robots.txt policy | `llms.txt` | AI UAs allowed (of 8) | Curated bytes exposed |
|---|---|---|---|---|
| [`before/`](before/) | blocks the AI crawlers | absent | **0** | **0** |
| [`after/`](after/) | allows the AI crawlers | present | **8** | **2868** |

Run it yourself:

```bash
bash reproduce.sh
```

No network, no browser, no LLM — it parses each variant's `robots.txt` to count how many known AI user-agents may fetch `/`, and measures the byte size of the curated `llms.txt` feed.

## Hypothesis

Making a site *accessible and extractable* to answer engines is a precondition for being cited. Two mechanical, controllable levers gate that access:

1. **robots.txt permission** — whether the answer-engine user-agents are allowed to fetch the site at all.
2. **A curated feed** — whether there is an `llms.txt` giving the crawler clean, quotable content instead of raw, navigation-cluttered HTML.

- **Independent variable:** the site's crawler policy (block + no feed → allow + feed).
- **Control (`before/`):** robots.txt blocks all 8 AI user-agents; no `llms.txt`.
- **Treatment (`after/`):** identical site, but robots.txt allows all 8 user-agents and a curated `llms.txt` is published.
- **Measured proxy:** number of AI user-agents allowed by robots.txt, and bytes of curated content exposed by `llms.txt`.

## How it was measured

See [`measurement.md`](measurement.md). In short: a stdlib-Python robots.txt evaluator selects the applicable group per user-agent (exact match, else `*`), resolves the rule for path `/` (longest match wins, `Allow` breaks ties), and counts how many of the 8 canonical AI crawlers come out allowed; `llms.txt` size is `os.path.getsize` (0 if absent). Numbers, date and sample in the file.

## What this proves — and what it doesn't

This measures **access and extractability**: whether an answer engine is *permitted* to fetch you, and whether you hand it curated, machine-readable content.

> **8 crawlers allowed + 2868 curated bytes ≠ being cited 8× more.**

Access is a *gate*, not a multiplier — a blocked or empty site cannot be quoted, but an allowed one is not automatically quoted either. Whether a passage is actually cited depends on relevance, authority and the engine's ranking, which this recipe does not measure. Proving that requires a separate live-LLM study (see Limitations in `measurement.md`).

## FAQ

**Do I have to name every AI bot?**
You control access per user-agent. Some operators publish more than one (Anthropic documents `ClaudeBot`, `Claude-User` and `Claude-SearchBot` — [source](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler); `anthropic-ai`, still common in 2023-era robots.txt files, is not in that list). This example tests a canonical set of 8; keep your list current from each operator's docs.

**Is `llms.txt` a standard crawlers obey today?**
It is an emerging convention ([llmstxt.org](https://llmstxt.org)), not a universally enforced spec. It costs almost nothing to publish and gives engines a clean extraction target; adoption is uneven and shifting — treat it as a low-cost bet, not a guarantee.

**Isn't allowing AI crawlers giving away my content?**
That is a business decision. If you want to be a cited source in AI answers, they have to be able to read you. If you don't, block them — but then don't expect citations.

---
<!-- ecosystem:start -->
Part of the **[GEO Cookbook](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook)** — reproducible examples for **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. Theory: **[Chapter 04 — Technical GEO](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook/blob/main/docs/04-technical.md)**. Hub: **[zentimes.es](https://zentimes.es)**. By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
