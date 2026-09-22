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
    template = ENGINES[engine]
    report = {
        "engine": engine,
        "when": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "controls": [],
    }
    all_passed = True
    for query, expected in CONTROLS:
        entry: dict = {"query": query, "expected_domain": expected}
        try:
            html, status = fetch(template.format(q=urllib.parse.quote_plus(query)))
        except Exception as exc:  # a transport failure is a failed control, not a crash
            entry.update(passed=False, error=f"{type(exc).__name__}: {exc}"[:200])
            report["controls"].append(entry)
            all_passed = False
            print(f"  {query[:44]:44} FAILED  ({entry['error'][:50]})")
            continue
        found = list(dict.fromkeys(domains(html)))
        passed = any(expected in d for d in found)
        all_passed &= passed
        entry.update(
            passed=passed,
            http_status=status,
            title=(re.search(r"<title>(.*?)</title>", html, re.S | re.I) or [None, ""])[1].strip()[:120],
            domains=found[:15],
            html_bytes=len(html),
        )
        report["controls"].append(entry)
        print(f"  {query[:44]:44} {'PASSED' if passed else 'FAILED'}  (expected {expected})")
        print(f"     returned: {', '.join(found)[:110] or '(no readable domains)'}")
    report["run_is_valid"] = all_passed
    return all_passed, report


if __name__ == "__main__":
    name = (sys.argv[1] if len(sys.argv) > 1 else "bing").lower()
    if name not in ENGINES:
        print(f"unknown engine {name!r}; known: {', '.join(ENGINES)}")
        raise SystemExit(2)
    print(f"=== answering control: {name} ===")
    ok, rep = run(name)
    print()
    print(
        "RUN IS VALID — the engine answered the control queries correctly."
        if ok
        else "RUN IS VOID — the engine returned pages that do not answer the control queries.\n"
        "Do not record observations collected in this state. They are not zeros."
    )
    out = f"answering-control-{name}.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    print(f"(raw result written to {out})")
    raise SystemExit(0 if ok else 1)
