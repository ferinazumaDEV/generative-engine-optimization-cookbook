# Probes — checks that decide whether a collection run counts

These are not measurements. They are the checks that decide whether a measurement is allowed to be recorded, and
they exist because of a specific afternoon documented in [PROTOCOL.md](../../PROTOCOL.md), section 13-ter: a
search engine answered every request promptly, with the right page title, no CAPTCHA and ten well-formed results
— for a different query each time. Nothing in the design as written would have refused that data.

| Probe | Question it answers | Exit status |
|---|---|---|
| [`engine-answering-control.py`](engine-answering-control.py) | Is the engine answering the query it was asked? | 0 valid, 1 void |
| [`network-is-clean.py`](network-is-clean.py) | Is this machine's view of the web intact, before any engine is blamed? | 0 clean, 1 not clean |

Standard library only. No browser, no account, no API key, no install:

```
python3 protocol/probes/engine-answering-control.py            # bing
python3 protocol/probes/engine-answering-control.py duckduckgo
python3 protocol/probes/network-is-clean.py
```

## The two rules they encode

**A control asserts a correct answer, not the absence of a refusal.** A control query is paired with a domain its
correct answer must contain. Checking only that the engine did not refuse passes an engine that confidently
returns someone else's results.

**Two control queries, and any one failing voids the run.** On 2026-09-21 at 15:47:08Z one control passed and the
other failed in the same run against the same engine. One control query would have declared that run valid.

## What "void" means

Discarded. A void run is not recorded as zeros, not kept as partial data, and not repaired by re-running only the
observations that look wrong. Scoring a blank as *not cited* manufactures an effect out of the collector's own
quota, and scoring a wrong-query page as *not cited* manufactures one out of the engine's.

## Expected results, and how to tell a real failure from a stale probe

`network-is-clean.py` reports the second engine as *corroborates*, *contradicts* or *inconclusive*, and only
*contradicts* counts against the machine. An engine that declines to answer — a rate limit, a challenge page, any
non-200 — is inconclusive by design: running these probes twice in quick succession is enough to trigger it, and
a check whose silence looks like its alarm is worse than no check.

If `engine-answering-control.py` fails, run `network-is-clean.py` before concluding anything about the engine.
