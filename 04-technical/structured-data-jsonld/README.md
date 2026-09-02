# Structured data (JSON-LD) — make your facts machine-readable

**A human reads your article fine without any markup. A machine reads *prose*, not *facts*.** Add a JSON-LD (schema.org) block and the same page suddenly exposes typed entities — a `Recipe`, its author as a `Person`, its steps as `HowToStep`s, its Q&A as a `FAQPage` — that an engine can extract, attribute and quote without inferring anything from the surrounding text.

> In this example, the plain page exposes **0** typed facts to a JSON-LD parser; the same article with a JSON-LD block exposes **37** typed facts across **17** typed entities — the *identical visible article*. Measured, dated and reproducible below.

## The technique in 30 seconds

- **Problem:** your author, publish date, ingredients, times and FAQ live only in prose and `<h2>`/`<li>` tags. A schema.org parser sees **no typed data** — every fact has to be guessed from natural language.
- **Fix:** add one `<script type="application/ld+json">` block describing the page as schema.org types (`Recipe`, `Person`, `Organization`, `FAQPage`, `BreadcrumbList`…). The visible page does not change at all.
- **Check yours:** run the page through any JSON-LD extractor (or `reproduce.sh` here). If it returns 0 typed facts, engines are reading your prose without any structured scaffolding.

## Hypothesis, variable, control, treatment

- **Hypothesis:** adding a JSON-LD block to a page increases the number of typed, machine-extractable facts a schema.org parser can read from it — without changing the human-visible content.
- **Independent variable:** presence of a `<script type="application/ld+json">` block (absent → present).
- **Control (`before/`):** the article page as plain HTML, no JSON-LD.
- **Treatment (`after/`):** the **same** article, byte-for-byte identical visible body, plus one JSON-LD `@graph`.
- **Held constant:** the headline, byline, prose, ingredient list, steps and FAQ are identical in both variants — so any difference is attributable only to the markup.

## Before / after

| Variant | JSON-LD | Typed entities | Typed facts a parser extracts |
|---|---|---|---|
| [`before/`](before/) | no | 0 | **0** |
| [`after/`](after/) | yes | 17 | **37** |

Both pages look identical to a human in a browser. Run it yourself:

```bash
bash reproduce.sh
```

No network, no browser, no LLM — it extracts the JSON-LD from each page's HTML source, parses it with `python3` stdlib, and counts the typed entities and typed facts.

## How it was measured

See [`measurement.md`](measurement.md). In short: pull every `application/ld+json` block from the HTML source, parse it as JSON, and count objects carrying an `@type` (entities) and the property assertions on them (facts). Method, numbers, tool and date are in the file.

## What this proves — and what it doesn't

This measures **typed facts a JSON-LD/schema.org parser can extract** — the *machine-readability* of your content. Nothing more.

> **37 extractable typed facts ≠ 37× more likely to be cited.**

Machine-readable structure is a *precondition and enabler* for clean extraction and attribution — not a proven multiplier on citation. Whether an engine actually quotes you still depends on relevance, authority and the engine's ranking. This recipe proves the facts become **structured and extractable**; it does **not** claim a citation rate. A causal claim needs a separate live-LLM test — see `measurement.md` → Limitations.

## FAQ

**Does JSON-LD change what users see?**
No. It lives in a `<script>` in the `<head>` (or body) and never renders. `before/` and `after/` are visually identical; only the machine layer differs.

**Isn't this just SEO rich-results markup?**
Same mechanism, different stakes. Classic SEO uses schema.org for rich snippets; in GEO the goal is that an engine can extract *typed facts into an answer* and attribute them, rather than paraphrasing your prose and dropping the source.

**Which schema types should I use?**
The ones that match the page: `Article`/`Recipe`/`Product`/`Event`, plus `Person`, `Organization`, `BreadcrumbList` and `FAQPage` where they apply. Keep the JSON-LD faithful to the visible content — mismatched or invented markup can hurt you.

---
<!-- ecosystem:start -->
Part of the **[GEO Cookbook](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook)** — reproducible examples for **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. By **[ferinazumaDEV](https://github.com/ferinazumaDEV)**.
<!-- ecosystem:end -->
