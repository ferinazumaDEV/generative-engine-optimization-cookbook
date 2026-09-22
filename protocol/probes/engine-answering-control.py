#!/usr/bin/env python3
"""Is the engine actually answering the query it was asked?

Run this at the start and at the end of every collection run. If it fails, the run is void: the
observations in between are not recorded as zeros, not kept as partial data, not scored at all.

Why a refusal check is not enough. On 2026-09-21 (addendum 13-ter of PROTOCOL.md) Bing served, from a
datacenter address, result pages with the right title, no CAPTCHA, no unusual-traffic text and ten
well-formed organic results that had nothing to do with the query -- a different unrelated set on every
request. An engine that refuses is easy to detect. An engine that answers confidently with someone
else's results is not, and scoring those pages produces data that looks clean and means nothing.

The control is positive and specific: a query whose correct answer must contain a named domain.

Each control reports one of three outcomes: **answered**, **wrong-query** (results came back and belong
to some other question), or **declined** (no results came back at all -- a non-200, a challenge page, a
transport failure). Both failures void the run. They are reported apart because an engine that refuses
and an engine that confidently answers the wrong question are different facts, and the finding in
section 13-ter depends on being able to say which one happened.

    python3 engine-answering-control.py            # checks Bing
    python3 engine-answering-control.py duckduckgo

Standard library only, no browser, no account, no API key. Exit status is 0 when every control passed
and 1 when any failed, so it can gate a run from a shell script.
"""
from __future__ import annotations

import gzip
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# A control query, and a domain its correct answer must contain. Both are deliberately boring:
# stable facts, canonical sources, no news, nothing that moves between runs.
CONTROLS = [
    ("caesium-137 half life wikipedia", "wikipedia.org"),
    ("python documentation sys module", "python.org"),
]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

ENGINES = {
    "bing": "https://www.bing.com/search?q={q}&setlang=en",
    "duckduckgo": "https://html.duckduckgo.com/html/?q={q}",
}


def fetch(url: str, timeout: int = 40) -> tuple[str, int]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
        return raw.decode("utf-8", "replace"), resp.status


def domains(html: str) -> list[str]:
    """Result domains, read from the display URL rather than the href.

    The href is a redirector on both engines, so the host of the href is the engine itself for every
    result -- a zero dressed up as data. The <cite> element carries the real display URL; DuckDuckGo's
    HTML endpoint additionally encodes the target in its uddg parameter.
    """
    out: list[str] = []
    for cite in re.findall(r"<cite[^>]*>(.*?)</cite>", html, re.S | re.I):
        plain = re.sub(r"<[^>]+>", "", cite).strip()
        m = re.match(r"(?:https?://)?([^/\s›]+)", plain)
        if m:
            out.append(re.sub(r"^www\.", "", m.group(1).lower()))
    for enc in re.findall(r"uddg=https?%3A%2F%2F([^%&\"]+)", html):
        out.append(re.sub(r"^www\.", "", enc.lower()))
    return out


def run(engine: str) -> tuple[bool, dict]:
    """Each control has three outcomes, not two.

    ``answered`` -- the expected domain is there.
    ``wrong-query`` -- the engine returned results, and they belong to some other question.
    ``declined`` -- the engine returned no results at all: a non-200, a challenge page, a transport
    failure. It did not answer, which is a different fact from answering badly.

    Both failing outcomes void the run, so the gate behaves identically. They are reported apart
    because the whole finding in PROTOCOL.md section 13-ter rests on telling them apart, and a probe
    that called a rate-limited HTTP 202 "the engine returned pages that do not answer the query"
    would be asserting something it did not observe.
    """
    template = ENGINES[engine]
    report = {
        "engine": engine,
        "when": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "controls": [],
    }
    for query, expected in CONTROLS:
        entry: dict = {"query": query, "expected_domain": expected}
        try:
            html, status = fetch(template.format(q=urllib.parse.quote_plus(query)))
        except Exception as exc:
            entry.update(outcome="declined", error=f"{type(exc).__name__}: {exc}"[:200])
            report["controls"].append(entry)
            print(f"  {query[:44]:44} DECLINED  (unreachable: {entry['error'][:40]})")
            continue
        found = list(dict.fromkeys(domains(html)))
        if status != 200 or not found:
            outcome = "declined"
        elif any(expected in d for d in found):
            outcome = "answered"
        else:
            outcome = "wrong-query"
        entry.update(
            outcome=outcome,
            http_status=status,
            title=(re.search(r"<title>(.*?)</title>", html, re.S | re.I) or [None, ""])[1].strip()[:120],
            domains=found[:15],
            html_bytes=len(html),
        )
        report["controls"].append(entry)
        label = {"answered": "ANSWERED", "wrong-query": "WRONG QUERY", "declined": "DECLINED"}[outcome]
        print(f"  {query[:44]:44} {label:11} (expected {expected})")
        if outcome == "declined":
            print(f"     HTTP {status}, {len(found)} readable results — the engine did not answer.")
        else:
            print(f"     returned: {', '.join(found)[:105]}")

    outcomes = [c["outcome"] for c in report["controls"]]
    valid = all(o == "answered" for o in outcomes)
    report["run_is_valid"] = valid
    report["verdict"] = (
        "valid" if valid else "void-wrong-query" if "wrong-query" in outcomes else "void-declined"
    )
    return valid, report


if __name__ == "__main__":
    name = (sys.argv[1] if len(sys.argv) > 1 else "bing").lower()
    if name not in ENGINES:
        print(f"unknown engine {name!r}; known: {', '.join(ENGINES)}")
        raise SystemExit(2)
    print(f"=== answering control: {name} ===")
    ok, rep = run(name)
    print()
    if ok:
        print("RUN IS VALID — the engine answered the control queries correctly.")
    elif rep["verdict"] == "void-wrong-query":
        print("RUN IS VOID — the engine returned results belonging to a different query.")
        print("Do not record observations collected in this state. They are not zeros.")
    else:
        print("RUN IS VOID — the engine did not answer: no results came back at all.")
        print("This is a refusal, not a wrong answer. Retry later; record nothing from it.")
    out = f"answering-control-{name}.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    print(f"(raw result written to {out})")
    raise SystemExit(0 if ok else 1)
