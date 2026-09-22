#!/usr/bin/env python3
"""Is this machine's view of the web intact, before any engine is blamed for anything?

Run this when a control fails. If the network itself is rewriting responses, every measurement taken
from this machine is contaminated, which is a far bigger finding than "one engine misbehaves" -- and
the two are indistinguishable from a single failing probe.

Three independent checks:

  1. Known content. A page whose text is known in advance must contain it. Decisive.
  2. A second engine, same address, same channel, same minute. Corroborating, and only decisive when it
     *contradicts*: an engine that answers correctly shows the address is not blocked and the query is
     answerable, while one that declines to answer at all (rate limit, challenge page, non-200) says
     nothing either way. Silence from a corroborating check is not evidence of a problem.
  3. Certificates. The hosts must present certificates issued to them. Decisive.

    python3 network-is-clean.py

Standard library only. Exit status 0 when all three pass.
"""
from __future__ import annotations

import gzip
import io
import json
import re
import socket
import ssl
import urllib.parse
import urllib.request
from datetime import datetime, timezone

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

KNOWN_PAGE = ("https://en.wikipedia.org/wiki/Caesium-137", ("half-life", "caesium"))
SECOND_ENGINE = ("https://html.duckduckgo.com/html/?q={q}", "caesium-137 half life wikipedia", "wikipedia.org")
HOSTS = ("www.bing.com", "en.wikipedia.org")


def fetch(url: str, timeout: int = 40) -> tuple[str, str, int]:
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
        return raw.decode("utf-8", "replace"), resp.geturl(), resp.status


def main() -> int:
    report: dict = {"when": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    ok = True

    print("=== 1. known content is served unaltered ===")
    url, terms = KNOWN_PAGE
    try:
        html, final, status = fetch(url)
        present = all(t in html.lower() for t in terms)
        ok &= present
        print(f"  HTTP {status}  final url {final[:70]}")
        print(f"  contains {' and '.join(terms)}: {'yes' if present else 'NO — the body is not this page'}")
        report["known_page"] = {"status": status, "final_url": final, "content_ok": present, "bytes": len(html)}
    except Exception as exc:
        ok = False
        print(f"  ERROR {type(exc).__name__}: {exc}")
        report["known_page"] = {"error": str(exc)[:200]}

    print("\n=== 2. a second engine answers the same control ===")
    # Three outcomes, not two. A second engine that declines to answer (rate limit, challenge page,
    # non-200) tells us nothing about the network, and treating its silence as a failure would raise a
    # false alarm about the machine every time this probe is run twice in quick succession. Only an
    # engine that answers with unrelated results contradicts check 1.
    template, query, expected = SECOND_ENGINE
    verdict = "inconclusive"
    try:
        html, _, status = fetch(template.format(q=urllib.parse.quote_plus(query)))
        found = [re.sub(r"^www\.", "", d.lower())
                 for d in re.findall(r"uddg=https?%3A%2F%2F([^%&\"]+)", html)]
        found = list(dict.fromkeys(found))
        if status != 200 or not found:
            verdict = "inconclusive"
            print(f"  HTTP {status}, {len(found)} readable domains — the second engine declined to answer.")
            print("  This says nothing about the network; checks 1 and 3 decide.")
        elif any(expected in d for d in found):
            verdict = "corroborates"
            print(f"  HTTP {status}  domains: {', '.join(found)[:105]}")
            print(f"  {expected} present: yes")
        else:
            verdict = "contradicts"
            print(f"  HTTP {status}  domains: {', '.join(found)[:105]}")
            print(f"  {expected} present: NO — a reachable engine returned unrelated results")
        report["second_engine"] = {"status": status, "verdict": verdict, "domains": found[:15]}
    except Exception as exc:
        print(f"  unreachable: {type(exc).__name__}: {exc}"[:110])
        print("  Inconclusive; checks 1 and 3 decide.")
        report["second_engine"] = {"verdict": "inconclusive", "error": str(exc)[:200]}
    if verdict == "contradicts":
        ok = False

    print("\n=== 3. certificates belong to the hosts ===")
    report["certificates"] = {}
    for host in HOSTS:
        try:
            ctx = ssl.create_default_context()
            # The default context still permits TLS 1.0 and 1.1. This check exists to detect
            # interception, so it must not itself accept a protocol version an interceptor could
            # downgrade the connection to.
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            with ctx.wrap_socket(socket.create_connection((host, 443), timeout=20), server_hostname=host) as s:
                cert = s.getpeercert()
            cn = dict(x[0] for x in cert["subject"]).get("commonName", "?")
            issuer = dict(x[0] for x in cert["issuer"]).get("organizationName", "?")
            print(f"  {host:20} CN={cn[:38]:38} issuer={issuer[:30]}")
            report["certificates"][host] = {"cn": cn, "issuer": issuer}
        except Exception as exc:
            ok = False
            print(f"  {host:20} ERROR {type(exc).__name__}: {exc}"[:110])
            report["certificates"][host] = {"error": str(exc)[:160]}

    report["network_is_clean"] = ok
    with open("network-is-clean.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    print()
    if ok and report.get("second_engine", {}).get("verdict") == "corroborates":
        print("NETWORK IS CLEAN — a failing engine control is about that engine, not this machine.")
    elif ok:
        print("NETWORK IS CLEAN as far as the decisive checks go: content is served unaltered and TLS is")
        print("intact. The second engine did not answer, so it neither corroborates nor contradicts.")
    else:
        print("NETWORK IS NOT CLEAN — fix this before drawing any conclusion about an engine.")
    print("(raw result written to network-is-clean.json)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
