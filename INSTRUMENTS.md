# The instruments

Every number in this cookbook is produced by one of six deterministic, offline
instruments — one per recipe, embedded in that recipe's `reproduce.sh`. This
file is their specification: what each one counts, what it deliberately does
not count, and how its definition has changed. `tests/test_instruments.py`
holds the conformance corpus (94 checks) that pins these definitions; four of
the six instruments are executed by the tests straight out of the recipe
scripts, so the corpus cannot drift from what the recipes run.

A number reproduced exactly says the instrument is deterministic. It does not
say the instrument measures what its name claims. Two of these were wrong for
weeks while reproducing their numbers perfectly (F06, F07 below); the history
sections exist so that nobody has to rediscover that.

Version and date conventions: "since 0.1.3" means the definition applies from
release v0.1.3 (2026-09-13) onward. Every change listed left **all 11 published
values unchanged** — the fixtures in this repository never contained the inputs
that defeated the earlier definitions. That is verified on every push by
rebuilding the dataset and comparing it record by record.

---

## 1. `ai-crawler-access` — AI-related robots.txt tokens allowed for `/`

**Counts.** Of eight AI-related user-agent tokens, how many `robots.txt`
allows to fetch the path `/`, following RFC 9309: a group applies to a token if
one of its `User-agent` lines names it (case-insensitive) or is `*` and no
specific group exists; within the applicable group, `*` in a pattern matches any
sequence, a trailing `$` anchors to the end of the path, the longest matching
pattern wins, and `Allow` wins an equal-length tie. An empty `Disallow:` allows
everything; an empty `Allow:` is a no-op.

**Does not count.** Whether the token is an HTTP crawler at all
(`Google-Extended` and `Applebot-Extended` are usage-control tokens with no
user-agent of their own), whether the site is actually crawled, or anything
about citation. The secondary measurement, bytes of `llms.txt`, is a size.

**History.**
- 0.1.0 – 0.1.2: patterns compared with `str.startswith`, so `*` and `$` were
  literal characters. `Disallow: /*` — the most common way to block a site —
  matched nothing and scored as *allowed*. Found by the external re-audit
  (F06), fixed 2026-09-12. Values unchanged: the fixtures use bare-path rules.
- 0.1.3: the metric renamed from *AI crawler user-agents* to *AI-related
  robots.txt tokens*, and each token carries its role and vendor documentation
  in the recipe.

## 2. `entity-clarity-sameas` — named entities resolved to one Wikidata Q-ID

**Counts.** Named entities declared in the page's `about` list whose `@id` or
`sameAs` contains exactly one URL of the form
`https://www.wikidata.org/wiki/Q<n>` or `https://www.wikidata.org/entity/Q<n>`
(with or without `www.`, http or https; leading and trailing whitespace
stripped), `Q<n>` being the whole final path segment and `n ≥ 1`.

**Does not count.** Property IDs (`P…`), URLs that merely contain a Q-ID
somewhere (a query parameter, a path suffix, a lookalike host), or two
different Q-IDs for one entity (that is ambiguity, not resolution).

**History.**
- 0.1.0 – 0.1.2: `re.search` with an unanchored pattern, so any string
  *containing* something Q-ID-shaped counted — including a URL not hosted on
  Wikidata. Found by the external re-audit (F07), fixed 2026-09-12: scheme,
  host and path are checked and the Q-ID must be the whole final segment.
  Values unchanged.

## 3. `chunk-friendly-structure` — self-contained chunks from a fixed-size splitter

**Counts.** The document is split by a standard recursive character splitter
(`chunk_size = 800`, no overlap, separators `["\n\n", "\n", " ", ""]`, greedy
packing of small pieces). A chunk is *self-contained* when it **starts clean**
— first non-blank character is a heading mark, list mark, quote mark, an
upper-case letter or a digit — **and ends clean** — ends with `.`, `!`, `?` or
`:`, or its last line is a heading. The denominator is the number of chunks.

**Does not count.** Semantic coherence, whether a retriever would rank the
chunk, or anything language-specific beyond the two boundary tests. A token
longer than 800 characters with no separator is hard-cut and counts as dirty on
both ends. An empty or whitespace-only document has zero chunks.

**History.**
- No definition change. Since 0.1.3 the definition is pinned by controls
  (empty document, one paragraph, headings without bodies, lowercase start, no
  terminal punctuation, one unbreakable token) and a metamorphic check on blocks
  sized so that each is exactly one chunk: reordering leaves the counts alone,
  doubling the document doubles them.

## 4. `ssr-vs-csr-rendering` — words a crawler that does not execute JavaScript can read

**Counts.** Whitespace-separated words left in the HTML **source** after
removing `<script>…</script>`, `<style>…</style>`, HTML comments, every tag,
and character entities (`&amp;`, `&#8212;`, `&#x2014;`), as `wc -w` counts
them.

**Does not count.** Text inside scripts (including JSON-LD blocks), styles,
comments or attribute values (`alt`, `title`). It **does** count `<noscript>`
content: that is exactly what a reader without JavaScript is served.

**History.**
- 0.1.0 – 0.1.2: only named entities (`&[a-z]+;`) were removed, so a numeric
  character reference counted as a visible word. Found by the conformance
  corpus, fixed 2026-09-13 (0.1.3). Values unchanged: the fixtures contain no
  entities at all.

## 5. `structured-data-jsonld` — typed facts and typed entities a JSON-LD parser extracts

**Counts.** Every `<script type="application/ld+json">` block on the page
(type attribute case-insensitive, single or double quotes) is parsed as JSON
and walked. A **typed entity** is an object carrying `@type` (a list of types
is still one entity). A **typed fact** is a key on a typed object other than
`@context` and `@type`. Untyped nested objects are neither entities nor facts,
though the key that holds them is a fact of their typed parent; `@graph`
wrappers are untyped and their members count.

**Does not count.** Blocks inside HTML comments (not on the page), blocks that
do not parse (a parser gets nothing from them; the other blocks still count),
scripts of any other type, and whether any of the facts is true.

**History.**
- 0.1.0 – 0.1.2: the raw HTML was scanned, so a commented-out block counted;
  and a single malformed block made `json.loads` raise and the whole
  measurement abort. Found by the conformance corpus, fixed 2026-09-13
  (0.1.3): comments stripped first, unparseable blocks skipped. Values
  unchanged: the fixture's one comment is prose, and both blocks parse.

## 6. `citation-anchoring` — claim→source pairs a deterministic parser extracts

**Counts.** Inside the `<!-- claims:start -->` … `<!-- claims:end -->` block
(the whole document if the markers are absent), a **claim** is a markdown list
item (`-` or `*`, any indentation) and a **pair** is a claim whose line carries
at least one inline markdown link `[text](http…)` or `[text](https…)`. The
denominator is the number of claims. Two links on one claim are one pair.

**Does not count.** `javascript:` and relative links, bare URLs, reference-style
links (`[text][1]`), links inside inline code or fenced code blocks (code is
quoted, not asserted), image embeds (`![alt](url)`), links outside the block,
links on lines that are not list items, and — pinned as scope, not as a
judgement — numbered list items.

**History.**
- 0.1.0 – 0.1.2: a list item inside a fenced code block counted as a claim, a
  link inside inline code counted as its source, and an image embed counted as
  a linkable source. Found by the conformance corpus, fixed 2026-09-13 (0.1.3).
  Values unchanged: the fixtures contain no code spans, fences or images.

**Integrity check: `unresolved_fragment_links`** (added after 0.1.4). Not a
measurement of the technique, and not in the dataset — the schema carries one
secondary measurement per recipe and this one's is `claims`. It is reported by
`reproduce.sh` (a line in the table, a `checks` entry in `--json`) and it
guards the pair count against one specific false positive: a claim whose link
points INTO the document at an `id` that is not there. As written, `#missing`
is relative and the pair count ignores it; but a pipeline that resolves
relative hrefs against the page URL first (which it must, to see relative
sources at all) turns it into `https://site/page#missing`, and the pair count
then scores it as a source. So the check runs on the hrefs **as written**.

It counts links on claim lines of the form `[text](#fragment)` and flags the
ones whose target does not resolve, following the HTML Standard's *find a
potential indicated element*: an element with that `id`, or an `<a>` with that
`name`; the fragment tried as written and percent-decoded; `#` and `#top` (any
case) are the top of the document even with no such element. Ids are
case-sensitive. An `id` declared twice is flagged, because a citation pointing
at it has no single target. It does not judge fragments into other documents
(they cannot be checked offline), does not count `data-id` or any attribute
that merely ends in `id`, and ignores ids and links inside fenced blocks or
inline code. Both fixtures: 0 fragment links, 0 unresolved.

Found in review: a `#`-link to a missing anchor scored as a perfect pair,
confirmed by hand. Controls written first
and seen failing against the recipe as it was; each rule was then broken on
purpose (existence ignored, case folded, duplicates accepted, every link
judged) and its own control went red. `claim_source_pairs` unchanged; the
dataset rebuilt byte-identical.

---

## How a change to an instrument is made

1. Add the failing control to `tests/test_instruments.py` first and watch it
   fail against the recipe as it is.
2. Change the recipe. For the four Python/bash instruments the test executes
   the recipe's own code, so there is nothing else to update; for the two
   copied matchers (robots, Wikidata) update the copy and let the drift check
   confirm it matches.
3. `bash dataset/build.sh` and check that `git status` shows no change under
   `dataset/` — or, if a value did change, stop: that is a dataset decision
   (new `schema_version`, a versioned change), never a silent fix.
4. Record the change here and in `CHANGELOG.md`, with the date and the
   sentence "values unchanged" only when step 3 proved it.
