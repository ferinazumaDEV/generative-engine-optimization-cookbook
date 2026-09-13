# Contributing

One maintainer, best-effort responses, no promised turnaround. Issues and pull requests are read.

## Before you open a pull request

```bash
python3 tests/test_instruments.py   # the six instruments against their conformance corpus
bash dataset/build.sh               # rebuild the dataset from the recipes
python3 dataset/validate.py         # the artifacts are consistent with each other
```

`git status` must be clean after the rebuild: a change that moves a published value is a dataset
decision (a new `schema_version`, a versioned change), never a side effect of a fix. See
[`INSTRUMENTS.md`](INSTRUMENTS.md) for how an instrument is changed.

Everything lands through a pull request with green CI. `main` is protected; nothing is pushed to it
directly, by anyone.

## Proposing a recipe

A recipe is a directory under its handbook chapter with `before/` and `after/` artifacts, a
`reproduce.sh` that measures both **offline, deterministically, with no LLM and no network**, prints
a table and — with `--json` — the numbers `dataset/build.sh` collects, and a `meta.yml` naming the
metric, its unit, the proxy it stands for, the sample size and the limitations. Look at any existing
recipe first; the six are the template. A recipe that needs an API key or a browser does not belong
here — it belongs in [`PROTOCOL.md`](PROTOCOL.md), as a preregistered study.

## Security

Report anything sensitive privately — see [`SECURITY.md`](SECURITY.md) — not in a public issue.
