#!/usr/bin/env python3
"""Conformance tests for the two measurement instruments.

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

These run with no network and no dependencies, like everything else here.
"""

import re
import sys

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

    total = len(ROBOTS_CASES) + len(WIKIDATA_CASES)
    if failures:
        sys.stderr.write(f"\nInstrument conformance FAILED -- {len(failures)} of {total}:\n")
        for f in failures:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print(f"instruments OK: {len(ROBOTS_CASES)} robots cases, "
          f"{len(WIKIDATA_CASES)} Wikidata cases, {total} total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
