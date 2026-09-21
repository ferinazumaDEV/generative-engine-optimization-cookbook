# Protocol — does machine legibility change citation by generative engines?

**Status: preregistered design, not yet run.** Version 1.0, 2026-09-13. No data
has been collected under this protocol. Nothing in this repository claims an
effect on any engine; this document says how such a claim *could* be earned,
and commits to the design before any result exists so the result cannot shape
it. It is registered externally through the Zenodo archive of the release that
carries it; the section *Registration* says how, and what that does and does
not guarantee.

Everything else in this cookbook measures **preconditions** — whether a page's
content is visible to a crawler that does not run JavaScript, whether its facts
are typed, whether its entities resolve. Those are offline, deterministic and
reproducible, and they say nothing about what an engine does with the page.
This protocol is the bridge between the two, and it is deliberately narrow.

## 1. Question

> For a page that exists in two variants identical in substance and different
> only in machine legibility — the `before/` and `after/` of a cookbook recipe —
> does the `after/` variant get cited by generative answer engines more often
> than the `before/` variant, for the same queries, over the same window?

One question. It is not "does GEO work"; it is whether one specific, offline-
measurable change moves one specific, observable outcome.

## 2. Hypotheses (fixed before any data)

- **H1.** Over the query panel and window, the `after/` variant is cited in a
  higher fraction of answers than the `before/` variant.
- **H0.** No difference, or a difference within the noise floor measured in
  section 7.

A result that fails to reject H0 is a result. It is reported the same way.

## 3. What is measured, per observation

One observation is one query, sent once, to one engine, on one date, from one
documented location and session state. For each, record:

| Field | Values |
|---|---|
| `variant_cited` | `before` / `after` / `both` / `neither` |
| `cited_urls` | every URL the answer attributes, verbatim |
| `position` | rank of our domain among cited sources, or `—` |
| `abstained` | the engine gave no answer or no sources (`true`/`false`) |
| `answer_hash` | SHA-256 of the answer text, for change detection |
| `screenshot` | file name |

The outcome is `variant_cited`. Everything else is context that lets a reader
audit the outcome or explain a surprise.

## 4. Treatment and control

Each recipe already ships a controlled pair: `before/` and `after/` differ in
exactly the property the recipe measures and in nothing else. Both variants are
hosted at stable, distinct URLs on the same domain, published on the same day,
with the same title, the same author and the same canonical-free status, so
that neither is preferred by anything other than the property under test.

Publishing the pair is a prerequisite, not part of the protocol, and it is
recorded: URL of each variant, date published, and the commit of this
repository they were built from.

## 5. Query panel (frozen before publication)

Twelve queries per recipe, written and committed **before** the pair is
published, in `protocol/queries/<recipe>.txt`. Half are questions the page
answers directly; half are adjacent questions where the page is one plausible
source among many. Queries are never edited after the panel is frozen; a query
that turns out to be malformed is dropped with a note, not replaced.

The panel is the unit of pre-registration: a study whose queries were chosen
after seeing which ones cite the page has measured its own selection.

## 6. Engines, conditions, window

- **Engines:** ChatGPT (with search), Perplexity, Google AI Overviews / AI
  Mode, Gemini, Copilot. An engine that cannot be observed under the stated
  conditions is reported as *not observed*, never inferred.
- **Conditions:** private session, no account, one named country, one named
  language, desktop web. All four are recorded per observation; any change
  starts a new series.
- **Window:** four dates, one per week, starting no earlier than 14 days after
  the pair is published (engines need to have crawled it — and *whether* they
  did is checked, section 8). Each query is sent once per engine per date.

That is 12 queries × 5 engines × 4 dates = **240 observations per recipe**, and
the study covers as many recipes as have a publishable pair — at least three.

## 7. Noise floor, measured first

Before comparing variants, the same panel is run twice on the same date, one
hour apart, against the *same* variant. The disagreement between the two runs
is the noise floor. A between-variant difference smaller than the noise floor
is reported as *within noise*, whatever its sign. This follows the design
argument in Schulte, Bleeker & Kaufmann (2026), *Don't Measure Once*
([arXiv:2604.07585](https://arxiv.org/abs/2604.07585)): a single observation of
an AI search result is not a measurement of a distribution.

## 8. What is checked before the data is believed

- **Crawl evidence.** Server logs for each variant's URL: which engine user-
  agents fetched it, when. A variant no engine has fetched cannot be cited, and
  a "no citation" for it is not evidence about legibility.
- **Reachability.** Both variants return 200, are not blocked in `robots.txt`
  for the engines under test, and render the same text with JavaScript off.
- **Panel integrity.** The committed query file's hash matches what was sent.

## 9. Analysis, decided now

Per recipe and per engine: the fraction of observations in which each variant
is cited, with a 95% interval (Wilson). The comparison is the difference of
fractions with its interval. Then the same pooled across engines, reported
*alongside* the per-engine figures, never instead of them — engines differ, and
a pooled number hides that.

There is no threshold for "success". The report states the difference, the
interval, the noise floor and the crawl evidence, and lets the reader judge.

**Exploratory analysis** — anything not in this section — is labelled as such
and kept in a separate part of the report.

## 10. What is published

The raw observation table (all fields of section 3, screenshots included), the
frozen query panel with its hash, the crawl-log extracts, the noise-floor runs,
and the analysis script. If any of those cannot be published, the report says
which and why, and the result is downgraded to *not independently checkable*.

## 11. What this protocol does not claim

- It does not measure ranking, traffic or business outcomes.
- It does not generalise beyond the recipes, engines, country, language and
  window stated. A result on three pages in one country in one month is a
  result on three pages in one country in one month.
- It does not make the offline measurements in this cookbook mean more than
  they do. They remain preconditions; this protocol tests whether one of them
  predicts an outcome, once.

## 12. Registration

This document being in git with a date is not preregistration; a commit can be
rewritten. Preregistration means a third party holds a timestamped copy that
the authors cannot alter. The route taken is the Zenodo archive of this
repository's tagged releases: every release from v0.1.1 onward is deposited by
Zenodo, which mints a version DOI under the concept DOI 10.5281/zenodo.22299279
and keeps the deposited files immutable. This document is part of release
v0.1.3, deposited **before the query panel is published** (the panel does not
exist yet). The version DOI is minted by Zenodo at deposit time and is listed on
the concept record's version list under v0.1.3; a later edit to this file lands
in a later release with its own DOI, so the registered text is the one in the
v0.1.3 record, not the one on `main`.

> Registered: release v0.1.3 of this repository, 2026-09-13, archived by Zenodo
> under concept DOI [10.5281/zenodo.22299279](https://doi.org/10.5281/zenodo.22299279)
> (version DOI: see the v0.1.3 entry on that record). Registered by the author,
> not by a third-party registry with review: the timestamp and immutability are
> Zenodo's; the design is not peer-reviewed.

## 13. Relationship to the earlier observation protocol

A separate, earlier note (4 September 2026) describes a one-pass observation of
citation *formatting* in minor engines, to replace two secondary-sourced
sentences in the handbook. That is a product-behaviour check: one pass, no
control, no repetition, and it says so. It is not a study and this protocol
does not subsume it. The two answer different questions and should not be
confused: that one asks *how* an engine cites; this one asks *whether* a change
we made alters *what* it cites.

## 13-bis. Addendum, 2026-09-21 — can these engines actually be observed?

Nothing above is rewritten. A pre-registration that is quietly edited is not one, so this is an addendum with a
date: what was measured, and what it means for the design as registered.

Section 6 names five engines and one hard condition — *private session, no account, one named country, one named
language, desktop web*. On 2026-09-21 each of them was requested once, from a datacenter address in Spain, in a
fresh browser context with no account, on a real (headed) browser:

| engine | what happened |
|---|---|
| Google AI Overviews / AI Mode | redirected to `google.com/sorry` — the unusual-traffic block. **Not observable from this address.** |
| Bing / Copilot | served a full results page with a generated answer. **Observable.** |
| Perplexity | redirected to `/search/new`; sign-in wall on the answer. **Not observable without an account.** |
| Gemini | sign-in wall. **Not observable without an account.** |
| ChatGPT with search | navigation timed out at 45 s. **Not observable.** |

So **four of the five engines this protocol registered cannot be observed under the conditions this protocol
itself sets**, and the fifth is blocked from a datacenter address. That is a defect in the registered design, found
before any data was collected rather than after, which is the only good time to find it.

**What Bing actually shows** (four queries, same day): a generated answer on all four, with a *sources strip* under
it and an attribution chip beside it (`Wikipedia +1`), and **no numbered or superscript markers inside the answer
text**. Under section 3's definition that is *sources listed, not inline citation* — the case section 3 already
says to record separately rather than score. One measurement gotcha for whoever writes the collector: every link
inside the answer block is a `bing.com` redirect, so the cited domain has to be resolved, not read off the href.

**Consequences for the next version of this protocol**, stated now so the revision is not retrofitted to the data:

1. The engine list has to be rewritten around what is observable, or the study needs accounts — and an account
   breaks the *private session, no account* condition, which exists so the observation is not personalised. That
   is a real trade-off and it belongs in the design, not in a footnote.
2. A residential address, or several, is a **precondition** and not an optimisation: Google is the largest surface
   in the design and it is unreachable from a server.
3. Whatever the final list is, the collector needs a **control query at the start and at the end of every run**.
   Measured the same day on a different engine: once a rate limit is hit, a query the engine refuses to answer is
   indistinguishable from one it answered without citing, and scoring the blank as *not cited* manufactures an
   effect out of the collector's own quota.

Raw data and the probe scripts ship with the ecosystem snapshot of the same date, under `evidencia/`.

## 13-ter. Addendum, 2026-09-21 afternoon — the observable engine answers the wrong query, intermittently and silently

Nothing above is rewritten, including 13-bis. 13-bis recorded, from probes around midday, that Bing/Copilot was
the one engine in section 6 observable from this address. Four hours later it was returning result pages that do
not answer the query asked, and the way it fails would have passed every check 13-bis specified.

### What was served

Between 15:30Z and 15:47Z, from the same datacenter address in Spain, requests to Bing came back with the
**right page title**, **no CAPTCHA**, **no unusual-traffic text**, a plausible `About N results`, and ten
well-formed organic results belonging to some entirely different query:

| query asked | domains returned in the top ten |
|---|---|
| how do I braise short ribs | `detail.chiebukuro.yahoo.co.jp`, `forums.commentcamarche.net` |
| how do I braise short ribs *(again, minutes later)* | `juraforum.de`, `123recht.de` |
| caesium-137 half life wikipedia | `webmail.sfr.fr`, `assistance.sfr.fr`, `espace-client.sfr.fr` |
| caesium-137 half life wikipedia *(again)* | `giallozafferano.it`, `cucinadelmuseo.it`, `soscuisine.com` |
| caesium-137 half life wikipedia *(15:47:08Z)* | `forum.chip.de` |
| python documentation sys module | `justwatch.com`, `skyshowtime.com`, `vod.tvp.pl` |
| python documentation sys module *(15:47:08Z)* | `python.org`, `w3schools.com`, `en.wikipedia.org` — **correct** |

Each page is internally coherent. It reads like a correct result page *for another query*, and the other query
differs on every request. No generated answer block appeared in any of them.

The last two rows are the important ones. **At the same moment, in the same run, one control query was answered
correctly and the other was not.** The failure is per-query and intermittent, not a state the address is in.

### Why this is not our client, and not our network

1. **Two independent clients.** A headed Chromium on a real X display, and plain `urllib` with a browser
   User-Agent and no cookies. Both got unrelated results. The browser profile is not the cause.
2. **Known content over the same channel.** `en.wikipedia.org/wiki/Caesium-137` returns the real article.
   Response bodies are not being rewritten in transit.
3. **A second engine, same address, same channel, same minute.** DuckDuckGo's HTML endpoint, asked the same
   control query at 15:46Z, returned `en.wikipedia.org` first. The address is not cut off and the query is
   answerable. Asked again a minute later it replied `HTTP 202` with no results of its own — which is a second
   engine declining, and says nothing either way.
4. **Certificates.** `www.bing.com` presents a Microsoft-issued certificate, `en.wikipedia.org` a Let's Encrypt
   one. Nothing is intercepting TLS.

What the mechanism is — a cache key collision, a routing fault, an anti-automation response that degrades rather
than refusing — is not determined here, and this addendum does not guess.

### What this changes in the design

**A control has to assert a correct answer, not the absence of a refusal.** 13-bis, consequence 3, asked for a
control query at the start and end of every run so a rate-limited blank is not scored as *not cited*. That
control passes this state completely: the engine is not refusing, it answers in under a second with ten results.

Two other plausible checks also fail to catch it:

- *Does the page depend on the query at all?* It does — the junk is different every time — so comparing
  unrelated queries against each other reports that everything is fine.
- *Did the control query pass?* At 15:47:08Z one did and one did not. **A single control query would have
  declared that run valid**, and every observation in it would have entered the dataset.

So the rule this addendum adds: **at least two control queries, each asserting a named domain its correct answer
must contain, at the start and at the end of every run. Any one of them failing voids the whole run.** A void run
is discarded, not recorded as zeros and not kept as partial data. `protocol/probes/engine-answering-control.py`
implements exactly this and exits non-zero so a run can be gated on it.

**Observability is a property of (engine, address, client, query, moment), not of an engine.** The table in
13-bis therefore reports a state at a timestamp, not a capability. Any run has to carry its own evidence that the
engine was answering while that run happened; establishing observability once and then collecting for weeks gives
no way to tell which observations are real.

**A corroborating check that goes quiet is not a failing check.** The first version of
`protocol/probes/network-is-clean.py` treated the second engine's `HTTP 202` as evidence that the network was
compromised, and announced it. Running a probe twice in a row was enough to produce that false alarm. A check
whose silence is indistinguishable from its alarm is the same defect this protocol keeps finding elsewhere, so
the second engine now reports *corroborates*, *contradicts* or *inconclusive*, and only *contradicts* counts
against the machine.

### A measurement gotcha, found by getting it wrong first

Both the cited links and the **organic** links on a Bing result page are `bing.com/ck/a?...&u=a1<base64url>`
redirectors. Reading the host off the `href` gives `bing.com` for all ten results. The first version of the
query-dependence check did that, compared the resulting domain sets across three unrelated queries, got a Jaccard
index of 1.00, and was one step away from reporting "the page does not depend on the query at all" — a finding
produced entirely by the collector's own bug. The target has to be decoded from the `u=a1` parameter, and a link
that cannot be decoded has to be recorded as unresolved rather than counted or silently dropped.

### What this does not show

It does not show that Bing is unobservable in general, from other addresses, or at other times — the correct
`python.org` result at 15:47:08Z is in the table precisely because it contradicts the simpler story. It does not
identify the mechanism. And it does not advance the question this protocol exists to answer: no citation data was
collected, and the study still has no result about machine legibility and citation.

What it adds is that the collector now refuses to record data from a run the engine was not answering — and that
the check which would have been written without this afternoon would not have refused anything.

Probes: [`protocol/probes/engine-answering-control.py`](protocol/probes/engine-answering-control.py) and
[`protocol/probes/network-is-clean.py`](protocol/probes/network-is-clean.py), standard library only, no account and no
API key. Raw output ships with the ecosystem snapshot of the same date under `evidencia/`.

## 14. Sources

- Aggarwal et al., *GEO: Generative Engine Optimization*, KDD 2024 —
  [arXiv:2311.09735](https://arxiv.org/abs/2311.09735). The controlled design
  this protocol borrows from, on a benchmark rather than live engines.
- Schulte, Bleeker & Kaufmann, *Don't Measure Once: Measuring Visibility in AI
  Search (GEO)*, 2026 — [arXiv:2604.07585](https://arxiv.org/abs/2604.07585).
  Why one observation is not a measurement.
- Wilson, E. B. (1927), *Probable inference, the law of succession, and
  statistical inference*, JASA 22(158) —
  [doi:10.1080/01621459.1927.10502953](https://doi.org/10.1080/01621459.1927.10502953).
  The interval used in section 9.
