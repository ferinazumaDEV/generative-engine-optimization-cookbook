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

## Dated notes

Additive notes, each dated. None of them changes the measured pair, the roster of 8 tested tokens or any published number.

### 2026-09-23 — vendor documentation re-checked

- Anthropic's crawler article now resolves at `support.claude.com` (the `support.anthropic.com` link above redirects there); it names `ClaudeBot`, `Claude-User` and `Claude-SearchBot` and still does not list `anthropic-ai` (Source)(https://support.claude.com/en/articles/8896518).
- Anthropic publishes its crawler IP prefixes as a JSON file: 26 prefixes, `creationTime` 2026-08-18T23:56:36Z when read on 2026-09-23 (Source)(https://claude.com/crawling/bots.json).
- Google's crawler list moved: the `google-common-crawlers` link above redirects to the `crawling/docs/crawlers-fetchers/` path. The page states that Google-Extended "doesn't have a separate HTTP request user agent string", that the token governs use of content for training Gemini models and for grounding, and that it "does not impact a site's inclusion in Google Search nor is it used as a ranking signal" (Source)(https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers).
- Apple's page states that disallowing `Applebot-Extended` opts a site out of training generative foundation models, and that the opt-out from "broad world knowledge answers" in Siri and Search is the `nosnippet` meta tag — a page-level control this recipe does not measure (Source)(https://support.apple.com/en-us/119829).
- Nuance to the headline sentence: blocking the eight tested tokens removes a site from the fetch pool of those crawlers; it does not decide every answer surface. Google-Extended does not govern Google Search inclusion (source above), Apple's answer opt-out is `nosnippet` (source above), and OpenAI documents `ChatGPT-User` for "certain user actions in ChatGPT" and `OAI-SearchBot` for search results as robots.txt settings independent of `GPTBot` (Source)(https://developers.openai.com/api/docs/bots).
- Perplexity's crawler page moved: the `guides/bots` link in `reproduce.sh` redirects to `docs/resources/perplexity-crawlers`, which documents `PerplexityBot` for search results ("not used to crawl content for AI foundation models") and `Perplexity-User` for user actions (Source)(https://docs.perplexity.ai/docs/resources/perplexity-crawlers).
- DuckDuckGo's `DuckAssistBot` is not among the 8 tested tokens. The vendor page states it crawls pages in real time for AI-assisted answers, that this data "is not used in any way to train AI models", that a robots.txt disallow takes effect after 72 hours, and that opting out does not impact organic search rankings (Source)(https://duckduckgo.com/duckduckgo-help-pages/results/duckassistbot/).
- The Bytespider source in `reproduce.sh` (bytedance.com/en/) is a corporate home page that does not mention the token when read on 2026-09-23; the `training` role assigned to it is tagged needs-verification (2026-09-23). The comment in `reproduce.sh` is not edited because the tests parse that file.
- Tokens documented by their operators today but not tested here (`OAI-SearchBot`, `ChatGPT-User`, `Claude-User`, `Claude-SearchBot`, `Perplexity-User`, `DuckAssistBot`): adding any of them changes the 8-of-8 figure and is a dataset decision (0.2.0, `schema_version` 3), tracked in `CHANGELOG.md`, not a note.
- contentsignals.org documents a robots.txt `Content-Signal:` directive with `yes`/`no` values for `ai-train`, `search` and `ai-input` (example: `Content-Signal: ai-train=no, search=yes, ai-input=no`) and states that not all automated systems honor it; the page prints no date (needs-verification, 2026-09-23; text rendered client-side, read from the page bundle on 2026-09-23). The `after/robots.txt` fixture carries no such line and the recipe does not measure it (Source)(https://contentsignals.org/).

### 2026-09-23 — llms.txt

- The format described above still matches the specification: an H1 as the only required section, a blockquote summary, Markdown sections of links, and an optional `Optional` section (Source)(https://llmstxt.org/).
- A server-log measurement of llms.txt discovery, self-archived on Zenodo with a DOI, not peer-reviewed (Hall, published 2026-09-17) reports 1,549 crawler requests for an `/ai/llms.txt` announced through a robots.txt `Sitemap:` directive and page-level HTML, across six sites and 165 site-days, against two requests for the un-announced root `/llms.txt`; the author declares a competing interest. The result is about discovery, not about any engine parsing or using the file (Source)(https://doi.org/10.5281/zenodo.22814844).
- The `# LLM-Content:` line in `after/robots.txt` is a comment, which robots.txt parsers ignore; the discovery routes that study measured are a `Sitemap:` line and an HTML link (source above). The fixture is not edited: its bytes belong to a published measurement pair.

---
<!-- ecosystem:start -->
Part of the **[GEO Cookbook](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook)** — reproducible examples for **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. Theory: **[Chapter 04 — Technical GEO](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook/blob/main/docs/04-technical.md)**. Hub: **[zentimes.es](https://zentimes.es)**. By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
