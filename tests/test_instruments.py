#!/usr/bin/env python3
"""Conformance tests for the six measurement instruments.

    python3 tests/test_instruments.py

Audit findings F06 and F07. Both recipes reproduced their published numbers
exactly, and both instruments were wrong anyway -- reproducing a number says the
script is deterministic, not that it measures what its name claims.

F06: the robots.txt matcher compared with ``str.startswith``, so the two special
characters of RFC 9309 were treated as ordinary text. ``Disallow: /*`` -- the
most common way to say "stay out" -- matched nothing, and the recipe reported
the path as ALLOWED. A false positive on a blocked site.

F07: the Wikidata matcher used ``re.search`` with an unanchored pattern, so any
string merely CONTAINING something Q-ID-shaped counted. A URL not even hosted on
Wikidata was accepted as a resolved entity.

The other four instruments (chunker, no-JS word count, JSON-LD extractor,
claim->source pairs) get the same treatment: negative controls -- inputs that
look like the thing being counted and must NOT count -- and one metamorphic
check each: reordering the units of a document leaves the count alone, and
concatenating a document with itself doubles it. A counter that fails either is
counting something other than what it says.

Those four are not copied into this file. Their code is read out of the recipe
scripts and executed here (the Python heredoc of each ``reproduce.sh``, or its
bash function), so what is tested is the recipe, by construction.

These run with no network and no dependencies beyond python3, bash and perl --
the same things the recipes themselves need.
"""

import json
import os
import re
import subprocess
import sys
import tempfile

# --- the two implementations under test, kept in step with the recipes ------ #

def robots_matches(pattern, path):
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    expr = "".join(".*" if ch == "*" else re.escape(ch) for ch in body)
    return re.match(expr + ("$" if anchored else ""), path) is not None


def robots_allowed(rules, path="/"):
    best_len, best_allow = -1, True
    for directive, value in rules:
        if value == "":
            if directive != "disallow":
                continue
            length, is_allow = 0, True
        else:
            if not robots_matches(value, path):
                continue
            length, is_allow = len(value), (directive == "allow")
        if length > best_len or (length == best_len and is_allow):
            best_len, best_allow = length, is_allow
    return best_allow


WIKIDATA = re.compile(r"^https?://(?:www\.)?wikidata\.org/(?:wiki|entity)/(Q[1-9][0-9]*)$")

# --- the corpus ------------------------------------------------------------ #

ROBOTS_CASES = [
    # (name, rules, path, expected_allowed)
    ("wildcard blocks everything",  [("disallow", "/*")],                "/",      False),
    ("bare slash blocks",           [("disallow", "/")],                 "/",      False),
    ("end anchor on root",          [("disallow", "/$")],                "/",      False),
    ("end anchor elsewhere",        [("disallow", "/x$")],               "/",      True),
    ("wildcard in the middle",      [("disallow", "/priv*ate")],         "/",      True),
    ("wildcard matches deep path",  [("disallow", "/a*")],               "/abc",   False),
    ("empty disallow allows all",   [("disallow", "")],                  "/",      True),
    ("empty allow is a no-op",      [("allow", "")],                     "/",      True),
    ("longer pattern wins",         [("disallow", "/*"), ("allow", "/")], "/",     False),
    ("allow breaks an equal tie",   [("disallow", "/a"), ("allow", "/a")], "/a",   True),
    ("no rule matches",             [("disallow", "/private")],          "/",      True),
    ("anchored exact match",        [("disallow", "/a$")],               "/a",     False),
    ("anchored does not prefix",    [("disallow", "/a$")],               "/ab",    True),
    ("dot is literal not regex",    [("disallow", "/a.c")],              "/abc",   True),
    ("plus is literal not regex",   [("disallow", "/a+")],               "/aaa",   True),
]

WIKIDATA_CASES = [
    ("canonical wiki URL",       "https://www.wikidata.org/wiki/Q42",                          True),
    ("entity URL, http",         "http://wikidata.org/entity/Q42",                             True),
    ("suffix after the Q-ID",    "https://wikidata.org/wiki/Q42-not-an-item",                  False),
    ("embedded in a query",      "https://example.invalid/?next=https://wikidata.org/wiki/Q42", False),
    ("trailing slash",           "https://wikidata.org/wiki/Q42/",                             False),
    ("Q0 is not an item",        "https://wikidata.org/wiki/Q0",                               False),
    ("host is a path segment",   "https://evil.com/wikidata.org/wiki/Q42",                     False),
    ("lookalike host",           "https://wikidata.org.evil.com/wiki/Q42",                     False),
    ("no scheme",                "wikidata.org/wiki/Q42",                                      False),
    ("a property, not an item",  "https://wikidata.org/wiki/P921",                             False),
    ("leading whitespace",       "  https://wikidata.org/wiki/Q42  ",                          True),
]


# --- the copies above must be the recipes' code, not a memory of it ---------- #
#
# The two matchers are re-implemented here because the recipes are bash scripts
# with embedded Python and cannot be imported. A copy can drift. So the drift is
# checked: the matching function body and the Wikidata pattern are read out of
# the recipe files and compared, character for character, with what this file
# tests. If a recipe changes, this test fails until the corpus is updated -- or
# until the recipe is changed back.

RECIPE_ROBOTS = "04-technical/ai-crawler-access/reproduce.sh"
RECIPE_WIKIDATA = "05-authority/entity-clarity-sameas/reproduce.sh"


def _recipe_text(path):
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "..", path), encoding="utf-8") as fh:
        return fh.read()


def _robots_matcher_body_in(text):
    m = re.search(r"anchored = pattern\.endswith\(\"\$\"\)\n.*?return re\.match\([^\n]*\n", text, re.S)
    return re.sub(r"^[ \t]+", "", m.group(0), flags=re.M) if m else None


def check_no_drift():
    problems = []
    recipe_body = _robots_matcher_body_in(_recipe_text(RECIPE_ROBOTS))
    local_body = _robots_matcher_body_in(open(__file__, encoding="utf-8").read())
    if not recipe_body or recipe_body != local_body:
        problems.append(f"robots matcher in {RECIPE_ROBOTS} differs from the copy tested here")
    m = re.search(r'WIKIDATA = re\.compile\(\n?\s*r"([^"]+)"', _recipe_text(RECIPE_WIKIDATA))
    if not m or m.group(1) != WIKIDATA.pattern:
        problems.append(f"Wikidata pattern in {RECIPE_WIKIDATA} differs from the copy tested here")
    return problems


# --- the other four instruments: executed straight out of the recipes -------- #
#
# Each of these recipes is ``python3 - <<'PY' ... PY`` (or a bash function) with
# the instrument's definitions first and the measurement of the fixtures after.
# The definitions are extracted and executed here; the measuring part is cut off
# at the first line that starts it (``rows = []`` / ``results = {}``). Nothing
# is copied, so nothing can drift: a change to a recipe is tested the moment it
# is made.

RECIPE_CHUNKER = "03-content/chunk-friendly-structure/reproduce.sh"
RECIPE_SSR = "04-technical/ssr-vs-csr-rendering/reproduce.sh"
RECIPE_JSONLD = "04-technical/structured-data-jsonld/reproduce.sh"
RECIPE_CITATION = "06-measurement/citation-anchoring/reproduce.sh"


def _embedded_python(recipe):
    text = _recipe_text(recipe)
    m = re.search(r"<<'PY'\n(.*?)\nPY\n", text, re.S)
    if not m:
        raise RuntimeError(f"{recipe}: no python heredoc found")
    code = m.group(1)
    cut = re.search(r"^(rows = \[\]|results = \{\})[ \t]*$", code, re.M)
    if not cut:
        raise RuntimeError(f"{recipe}: could not find where the measurement starts")
    namespace = {"__name__": f"recipe_{os.path.basename(os.path.dirname(recipe))}"}
    exec(compile(code[:cut.start()], recipe, "exec"), namespace)
    return namespace


def _bash_function(recipe, name):
    m = re.search(rf"^{name}\(\) \{{\n.*?^\}}\n", _recipe_text(recipe), re.S | re.M)
    if not m:
        raise RuntimeError(f"{recipe}: no bash function {name}()")
    return m.group(0)


def _write(directory, name, content):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def words_visible(html_path):
    """The recipe's ``extract`` piped into ``wc -w``, exactly as reproduce.sh does."""
    script = _bash_function(RECIPE_SSR, "extract") + '\nextract "$1" | wc -w\n'
    out = subprocess.run(["bash", "-c", script, "_", html_path],
                         capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


# --- the corpus for the other four --------------------------------------------- #

LD = '<script type="application/ld+json">%s</script>'

JSONLD_CASES = [
    # (name, html, expected_typed_entities, expected_typed_facts)
    ("one typed object, two facts",
     LD % '{"@context":"https://schema.org","@type":"Person","name":"A","url":"https://a.b"}', 1, 2),
    ("@context and @type are not facts",
     LD % '{"@context":"https://schema.org","@type":"Thing"}', 1, 0),
    ("@type given as a list is one entity, not two",
     LD % '{"@type":["Person","Author"],"name":"A"}', 1, 1),
    ("@graph: the wrapper is untyped, its members count",
     LD % '{"@context":"https://schema.org","@graph":[{"@type":"Person","name":"A"},'
          '{"@type":"Organization","name":"B","url":"u"}]}', 2, 3),
    ("an untyped nested value is not an entity and carries no facts",
     LD % '{"@type":"Person","name":"A","address":{"streetAddress":"S","postalCode":"P"}}', 1, 2),
    ("an @id-only reference is not an entity",
     LD % '{"@type":"Article","author":{"@id":"#me"}}', 1, 1),
    ("typed objects inside a list value count",
     LD % '{"@type":"Article","author":[{"@type":"Person","name":"A"},{"@type":"Person","name":"B"}]}', 3, 3),
    ("a top-level scalar is not an entity",
     LD % '"just a string"', 0, 0),
    ("a block that does not parse contributes nothing; the others still count",
     LD % '{"@type": "Person", "name": }' + LD % '{"@type":"Thing","name":"T"}', 1, 1),
    ("an empty block contributes nothing",
     LD % '   ', 0, 0),
    ("a commented-out block is not on the page",
     "<!-- " + LD % '{"@type":"Person","name":"A"}' + " -->", 0, 0),
    ("a page with no JSON-LD",
     "<html><body><p>Hello</p></body></html>", 0, 0),
    ("a script of another type is not JSON-LD",
     '<script type="application/json">{"@type":"Person","name":"A"}</script>', 0, 0),
    ("the type attribute is case-insensitive and may be single-quoted",
     "<script type='APPLICATION/LD+JSON'>{\"@type\":\"Thing\",\"name\":\"T\"}</script>", 1, 1),
]

JSONLD_RICH = (LD % '{"@context":"https://schema.org","@type":"Article","headline":"H","author":'
                    '{"@type":"Person","name":"A","sameAs":["https://x.y"]}}')
JSONLD_OTHER = LD % '{"@type":"Organization","name":"O","url":"https://o.org"}'

CHUNK_CASES = [
    # (name, document, expected_chunks, expected_self_contained)
    ("empty document",                          "",                                             0, 0),
    ("whitespace only",                         " \n\n \n",                                     0, 0),
    ("one clean paragraph",                     "The quick brown fox jumps over the lazy dog.", 1, 1),
    ("a lowercase start is not clean",          "the quick brown fox jumps over the lazy dog.", 1, 0),
    ("no terminal punctuation is not clean",    "The quick brown fox jumps over the lazy dog",  1, 0),
    ("headings without bodies",                 "# One\n\n# Two\n\n# Three",                    1, 1),
    ("a list item is a clean start",            "- item one is here.",                          1, 1),
    ("a quote is a clean start",                "> Quoted sentence.",                           1, 1),
    ("a digit is a clean start",                "2024 was a year.",                             1, 1),
    ("a colon is a clean end",                  "Consider the following:",                      1, 1),
    ("one unbreakable token beyond the size is hard-cut, and dirty", "x" * 900,                2, 0),
]

# Blocks sized so that no two ever fit in one 800-character chunk: each block is
# then exactly one chunk, whatever the order, and the count is a count of blocks.
CHUNK_BLOCKS = [
    "A" + "a" * 498 + ".",       # clean start, clean end
    "b" * 500,                   # dirty both ways
    "C" + "c" * 499,             # clean start, dirty end
    "D" + "d" * 498 + ".",       # clean start, clean end
]

B = "<!-- claims:start -->\n%s\n<!-- claims:end -->"

CITATION_CASES = [
    # (name, markdown, expected_claims, expected_claim_source_pairs)
    ("empty document",                                    "",                                          0, 0),
    ("no markers: the whole document is the block",       "- A [s](https://e.com)\n- B",              2, 1),
    ("a javascript: link is not a source",                B % "- A [x](javascript:alert(1))",          1, 0),
    ("a relative link is not a source",                   B % "- A [x](/docs/proof)",                  1, 0),
    ("a bare URL is not an inline link",                  B % "- A https://e.com/proof",               1, 0),
    ("a reference-style link is not inline",              B % "- A [x][1]\n\n[1]: https://e.com",      1, 0),
    ("a link inside inline code is not a source",         B % "- A `[x](https://e.com)`",              1, 0),
    ("a list inside a fenced code block is not claims",
     B % "```\n- not a claim [x](https://e.com)\n```\n- Real claim [y](https://e.com)",                 1, 1),
    ("an image is not a linkable source",                 B % "- A ![alt](https://e.com/i.png)",       1, 0),
    ("a link outside the block does not count",           "Intro [x](https://e.com)\n" + B % "- A",   1, 0),
    ("a claim with two links is one pair",                B % "- A [x](https://e.com) and [y](https://f.com)", 1, 1),
    ("a non-list line with a link is not a claim",        B % "Plain [x](https://e.com)",              0, 0),
    ("http and https both count",                         B % "- A [x](http://e.com)\n- B [y](https://e.com)", 2, 2),
    ("a URL with whitespace is not a link",               B % "- A [x](https://e.com/a b)",            1, 0),
    ("nested list items are claims too",                  B % "- A\n  - B [x](https://e.com)",         2, 1),
    ("scope, pinned: numbered items are not counted",     B % "1. A [x](https://e.com)",               0, 0),
]

CITATION_LINES = [
    "- One [s](https://one.example)",
    "- Two",
    "* Three [s](https://three.example) and [t](https://t.example)",
    "- Four https://bare.example",
]

# The fragment check rides on the same claims block. It answers one question the
# pair count cannot: when a claim's link points INTO this document (``#id``),
# does that id exist exactly once? A pipeline that resolves relative hrefs
# against the page URL before counting turns ``#missing`` into
# ``https://site/page#missing`` -- and then the pair count scores it as a source.
# Resolution follows the HTML Standard's "find a potential indicated element":
# an element with that id or an <a> with that name, the fragment tried as
# written and percent-decoded, and ``#`` / ``#top`` meaning the top of the
# document even with no such element. A duplicated id is flagged: ids must be
# unique, so a citation pointing at one has no single target.

FRAGMENT_CASES = [
    # (name, markdown, expected_fragment_links, expected_unresolved)
    # -- must be flagged (negative controls) --
    ("a fragment with no such id",                  B % "- A [x](#missing)",                                   1, 1),
    ("an id that differs only in case",             B % "- A [x](#section)" + '\n<h2 id="Section">S</h2>',   1, 1),
    ("an id that is declared twice",                B % "- A [x](#dup)" + '\n<p id="dup">1</p><p id="dup">2</p>', 1, 1),
    ("data-id is not an id",                        B % "- A [x](#t)" + '\n<p data-id="t">T</p>',            1, 1),
    ("an id inside a fenced block is not an element",
     B % "- A [x](#t)" + '\n```\n<p id="t">T</p>\n```',                                                      1, 1),
    ("an id inside inline code is not an element",  B % "- A [x](#t)" + '\n`<p id="t">T</p>`',              1, 1),
    # -- must NOT be flagged --
    ("a link without a fragment is not broken",     B % "- A [x](https://e.com)\n- B [y](/docs/proof)",      0, 0),
    ("a fragment into ANOTHER document is not judged", B % "- A [x](https://e.com/page#nope)",               0, 0),
    ("an id that exists once resolves",             B % "- A [x](#t)" + '\n<h2 id="t">T</h2>',               1, 0),
    ("single quotes and unquoted ids resolve",      B % "- A [x](#a)\n- B [y](#b)" + "\n<p id='a'>A</p><p id=b>B</p>", 2, 0),
    ("an <a name> resolves",                        B % "- A [x](#n)" + '\n<a name="n"></a>',                1, 0),
    ("an empty fragment is the top of the document", B % "- A [x](#)",                                       1, 0),
    ("#top is the top of the document",             B % "- A [x](#top)\n- B [y](#TOP)",                      2, 0),
    ("a percent-encoded fragment is decoded",       B % "- A [x](#caf%C3%A9)" + '\n<p id="café">C</p>',      1, 0),
    ("an image is not a link",                      B % "- A ![alt](#missing)",                              0, 0),
    ("a fragment link off a claim line is not counted", B % "Plain [x](#missing)\n- A",                      0, 0),
    ("a fragment link in inline code is not counted", B % "- A `[x](#missing)`",                             0, 0),
    ("the id may live outside the claims block",    '<h2 id="t">T</h2>\n' + B % "- A [x](#t)",               1, 0),
]

FRAGMENT_TARGETS = '\n<h2 id="one">1</h2><h2 id="two">2</h2>'
FRAGMENT_LINES = [
    "- One [s](#one)",
    "- Two [s](#nowhere)",
    "* Three [s](#two) and [t](#gone)",
    "- Four [s](https://e.com)",
]

SSR_CASES = [
    # (name, html, expected_words)
    ("plain paragraph",                              "<p>one two three</p>",                                  3),
    ("inline script content is not text",            "<p>one</p><script>var a = 'two three four';</script>",  1),
    ("script with attributes across lines",          "<p>one</p><script type=\"module\"\n src=\"x.js\">two three</script>", 1),
    ("style content is not text",                    "<style>.a { color: red }</style><p>one</p>",            1),
    ("an HTML comment is not text",                  "<!-- one two --><p>three</p>",                          1),
    ("attribute values are not text",                "<img alt=\"one two\" title=\"three\"><p>four</p>",      1),
    ("a named entity is not a word",                 "<p>one &amp; two</p>",                                  2),
    ("a numeric character reference is not a word",  "<p>one &#8212; two &#x2014; three</p>",                 3),
    ("a JSON-LD block is not visible text either",   LD % '{"name":"one two"}' + "<p>three</p>",              1),
    ("tag names in upper case",                      "<SCRIPT>one</SCRIPT><P>two</P>",                        1),
    ("text split by tags is still separate words",   "<b>one</b><i>two</i>",                                  2),
    ("noscript content IS what a no-JS reader is served", "<noscript><p>one two</p></noscript>",              2),
    ("empty page",                                   "",                                                      0),
]

SSR_PARTS = [
    "<h1>Title words here</h1>",
    "<p>A paragraph of five words.</p>",
    "<script>var hidden = 'not counted at all';</script>",
    "<ul><li>item</li><li>another item</li></ul>",
]


# --- running the corpus ---------------------------------------------------------- #

def _check(failures, label, got, expected):
    if got != expected:
        failures.append(f"{label}: got {got}, expected {expected}")


def run_jsonld(failures, tmp):
    count = _embedded_python(RECIPE_JSONLD)["count"]
    for i, (name, html, ents, facts) in enumerate(JSONLD_CASES):
        try:
            got = count(_write(tmp, f"ld{i}.html", html))
        except Exception as exc:  # a crash is a failed control, not a crashed suite
            got = f"raised {type(exc).__name__}"
        _check(failures, f"jsonld/{name}", got, (ents, facts))
    one = count(_write(tmp, "ld-one.html", JSONLD_RICH + JSONLD_OTHER))
    swapped = count(_write(tmp, "ld-swapped.html", JSONLD_OTHER + JSONLD_RICH))
    doubled = count(_write(tmp, "ld-doubled.html", (JSONLD_RICH + JSONLD_OTHER) * 2))
    _check(failures, "jsonld/metamorphic: reordering the blocks", swapped, one)
    _check(failures, "jsonld/metamorphic: doubling the page", doubled, (one[0] * 2, one[1] * 2))
    return len(JSONLD_CASES) + 2


def run_chunker(failures, tmp):
    measure = _embedded_python(RECIPE_CHUNKER)["measure"]
    for i, (name, doc, chunks, sc) in enumerate(CHUNK_CASES):
        _check(failures, f"chunker/{name}", measure(_write(tmp, f"ch{i}.md", doc)), (chunks, sc))
    base = measure(_write(tmp, "ch-base.md", "\n\n".join(CHUNK_BLOCKS)))
    _check(failures, "chunker/metamorphic: every block is one chunk", base, (4, 2))
    for j, order in enumerate((CHUNK_BLOCKS[::-1], CHUNK_BLOCKS[1:] + CHUNK_BLOCKS[:1])):
        got = measure(_write(tmp, f"ch-perm{j}.md", "\n\n".join(order)))
        _check(failures, f"chunker/metamorphic: reordering the blocks ({j})", got, base)
    doubled = measure(_write(tmp, "ch-doubled.md", "\n\n".join(CHUNK_BLOCKS * 2)))
    _check(failures, "chunker/metamorphic: doubling the document", doubled, (base[0] * 2, base[1] * 2))
    return len(CHUNK_CASES) + 4


def run_citation(failures, tmp):
    analyze = _embedded_python(RECIPE_CITATION)["analyze"]
    for i, (name, md, claims, pairs) in enumerate(CITATION_CASES):
        _check(failures, f"citation/{name}", analyze(_write(tmp, f"ci{i}.md", md)), (claims, pairs))
    base = analyze(_write(tmp, "ci-base.md", B % "\n".join(CITATION_LINES)))
    _check(failures, "citation/metamorphic: the base block", base, (4, 2))
    swapped = analyze(_write(tmp, "ci-swapped.md", B % "\n".join(CITATION_LINES[::-1])))
    _check(failures, "citation/metamorphic: reordering the claims", swapped, base)
    doubled = analyze(_write(tmp, "ci-doubled.md", B % "\n".join(CITATION_LINES * 2)))
    _check(failures, "citation/metamorphic: doubling the block", doubled, (base[0] * 2, base[1] * 2))
    return len(CITATION_CASES) + 3


def run_fragments(failures, tmp):
    recipe = _embedded_python(RECIPE_CITATION)
    check = recipe.get("unresolved_fragments")
    if check is None:
        failures.append(f"fragments: {RECIPE_CITATION} defines no unresolved_fragments()")
        return len(FRAGMENT_CASES) + 3
    for i, (name, md, links, unresolved) in enumerate(FRAGMENT_CASES):
        _check(failures, f"fragments/{name}", check(_write(tmp, f"fr{i}.md", md)), (links, unresolved))
    base = check(_write(tmp, "fr-base.md", B % "\n".join(FRAGMENT_LINES) + FRAGMENT_TARGETS))
    _check(failures, "fragments/metamorphic: the base block", base, (4, 2))
    swapped = check(_write(tmp, "fr-swapped.md", B % "\n".join(FRAGMENT_LINES[::-1]) + FRAGMENT_TARGETS))
    _check(failures, "fragments/metamorphic: reordering the claims", swapped, base)
    # The targets stay declared once: doubling them would duplicate every id,
    # which is a different document, not the same one twice.
    doubled = check(_write(tmp, "fr-doubled.md", B % "\n".join(FRAGMENT_LINES * 2) + FRAGMENT_TARGETS))
    _check(failures, "fragments/metamorphic: doubling the claims", doubled, (base[0] * 2, base[1] * 2))
    # The pair count must not move because of this check: same inputs, same pairs.
    analyze = recipe["analyze"]
    _check(failures, "fragments/claim_source_pairs untouched",
           analyze(_write(tmp, "fr-pairs.md", B % "\n".join(FRAGMENT_LINES) + FRAGMENT_TARGETS)), (4, 1))
    return len(FRAGMENT_CASES) + 4


def run_ssr(failures, tmp):
    for i, (name, html, words) in enumerate(SSR_CASES):
        _check(failures, f"ssr/{name}", words_visible(_write(tmp, f"ssr{i}.html", html)), words)
    base = words_visible(_write(tmp, "ssr-base.html", "".join(SSR_PARTS)))
    _check(failures, "ssr/metamorphic: the base page", base, 11)
    swapped = words_visible(_write(tmp, "ssr-swapped.html", "".join(SSR_PARTS[::-1])))
    _check(failures, "ssr/metamorphic: reordering the parts", swapped, base)
    doubled = words_visible(_write(tmp, "ssr-doubled.html", "".join(SSR_PARTS * 2)))
    _check(failures, "ssr/metamorphic: doubling the page", doubled, base * 2)
    return len(SSR_CASES) + 3


def main():
    failures = []

    for name, rules, path, expected in ROBOTS_CASES:
        got = robots_allowed(rules, path)
        if got != expected:
            failures.append(f"robots/{name}: path {path!r} -> allowed={got}, expected {expected}")

    for name, url, expected in WIKIDATA_CASES:
        got = WIKIDATA.match(url.strip()) is not None
        if got != expected:
            failures.append(f"wikidata/{name}: {url!r} -> accepted={got}, expected {expected}")

    failures.extend(check_no_drift())

    with tempfile.TemporaryDirectory() as tmp:
        others = run_jsonld(failures, tmp) + run_chunker(failures, tmp) \
            + run_citation(failures, tmp) + run_fragments(failures, tmp) \
            + run_ssr(failures, tmp)

    total = len(ROBOTS_CASES) + len(WIKIDATA_CASES) + 2 + others
    if failures:
        sys.stderr.write(f"\nInstrument conformance FAILED -- {len(failures)} of {total}:\n")
        for f in failures:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print(f"instruments OK: {len(ROBOTS_CASES)} robots cases, "
          f"{len(WIKIDATA_CASES)} Wikidata cases, 2 drift checks, "
          f"{others} controls and metamorphic checks on the other four instruments, "
          f"{total} total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
