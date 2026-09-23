# Releasing

A release of this repository is not a software release. It is a **citable version**: the tag becomes an archived
deposit on Zenodo with its own DOI, and that deposit is what someone cites, downloads and checks a claim against.
Everything below exists so that the deposit and the tag cannot drift apart.

## The rule that is different here

**In this repository you create the GitHub Release by hand. That is the step that mints the DOI.**

There is no `release.yml`. The Zenodo integration is a repository webhook subscribed to the `release` event: it
fires when the Release is published, takes a snapshot of the tag, and mints a version DOI.

This is the **opposite** of the rule in the five package repositories (`typedout`, `politeclient`, `scaffld`,
`webhook-replay`, `framesig`), where `release.yml` creates the Release itself and creating it by hand breaks the
run *after* it has already published to PyPI. Getting the two backwards is how two package releases had to be
repaired by hand on 14 September 2026. Before releasing anything, check which kind of repository you are in:

| | this repository | a package repository |
|---|---|---|
| has `.github/workflows/release.yml` | no | yes |
| who creates the GitHub Release | **you** | the workflow |
| what the tag triggers | nothing | the whole release run |
| what the Release triggers | the Zenodo deposit | nothing |

## When a release is warranted

Publish a version when the change **reaches a reader**: corrected or withdrawn claims, new or revised recipes,
new measurements, a dated addendum to `PROTOCOL.md`. Continuous integration, internal tooling, formatting and
dependency pins do not reach a reader and do not justify a version.

`main` sitting ahead of the latest tag is therefore a normal, deliberate state, not a backlog.

## Steps

### 1. The preparation pull request

One pull request that moves every version string at once. In this repository the version lives in four places:

| file | what to change |
|---|---|
| `CITATION.cff` | `version:` and `date-released:` (the release date, ISO `YYYY-MM-DD`) |
| `about.jsonld` | the `"version"` field |
| `README.md` | the `Version` row of the table |
| `CHANGELOG.md` | promote `## [Unreleased]` to `## [X.Y.Z] — YYYY-MM-DD` and open a fresh `## [Unreleased]` |

Two things that have failed before and will fail again:

- **Do not link the tag from the README.** `releases/tag/vX.Y.Z` does not exist while the pull request is open, so
  the link check fails on the very pull request that prepares the release. Link the releases page instead, which
  never 404s and always shows the newest version. This failed exactly that way on v0.1.2.
- **Keep every scalar in `CITATION.cff` a scalar.** A list where a string is expected (a `license:` written as a
  list, for instance) makes the deposit fail its own metadata validation. This happened to the cookbook's v0.1.0
  on 4 September 2026.

The `dataset` workflow cross-checks the citation scalars, so let CI decide rather than reading the diff.

### 2. Merge, and let CI finish on `main`

Do not tag a commit whose checks have not completed on `main`.

### 3. Create the tag on the merge commit

```
gh api -X POST repos/ferinazumaDEV/generative-engine-optimization-cookbook/git/refs \
  -f ref=refs/tags/vX.Y.Z -f sha=<merge sha>
```

Nothing happens yet. In this repository the tag is a label, not a trigger.

### 4. Publish the GitHub Release — this mints the DOI

```
gh release create vX.Y.Z -R ferinazumaDEV/generative-engine-optimization-cookbook \
  --title "vX.Y.Z" --notes-file <notes>
```

The notes say what changed for a reader, in the words of the changelog entry, and nothing about the tooling.

### 5. Verify at the destination, not at the sender

A published Release is not evidence that the deposit exists. Ask Zenodo:

```
python3 - <<'PY'
import json, urllib.request
rid = "22299279"   # concept record id for this work
req = urllib.request.Request(f"https://zenodo.org/api/records/{rid}",
                             headers={"User-Agent": "Mozilla/5.0 (compatible; release-check/1.0)"})
d = json.load(urllib.request.urlopen(req, timeout=40))
print(d["metadata"]["version"], d["doi"], d.get("conceptdoi"))
PY
```

`metadata.version` must equal the tag you just pushed, and `doi` is the new version DOI. The concept DOI
(`10.5281/zenodo.22299279`), which is what `CITATION.cff` carries, stays the same forever and always resolves to
the newest version — that is why it is the one to cite.

Two ways this check has misled before, both worth knowing:

- Querying `zenodo.org/api/records?q=doi:"..."` with the concept DOI returns **zero hits**, because the concept
  DOI is not any single record's `doi` field. Zero hits there proves nothing. Fetch the record by id instead.
- The repository's webhook delivery log can be empty even for a delivery that succeeded. It is not evidence
  either way. Zenodo is the destination; ask Zenodo.

Then check the deposit against the tag **by content**: every file in the archive must have the same SHA-256 as
the file at that tag. A DOI that resolves says a deposit exists, not that it contains what you tagged.

### 6. Software Heritage

Zenodo forwards the archive, but indexing is not immediate and the origin API returns `NotFoundExc` while it
catches up — a false negative, not a missing deposit. To be sure, trigger it and record the result in the release
notes:

```
curl -s -X POST "https://archive.softwareheritage.org/api/1/origin/save/git/url/https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook/"
```

### 7. Tell the mirrors, because their guards cannot see this

At least one public tool reproduces four of this repository's metrics and states on its page **"cross-checked on
<date> with cookbook <version>"** — the AI citability inspector on zentimes.es, whose ids `words_visible_no_js`,
`typed_entities`, `ai_user_agents_allowed` and `llms_txt_bytes` are this cookbook's. Its deploy guard fails when
that statement is older than 120 days, which stops it ageing silently. **It cannot detect that a new version of
this cookbook exists.** If you tag today and say nothing, that page will keep saying it matches a version that is
no longer current for up to 119 more days, with a green guard the whole time.

So a release here is not finished until the mirror is told. Send the version and the date to whoever runs the
mirror, and the cross-check is repeated the same day with `compara-inspector-vs-recetas.py`: four of four, or the
statement comes down. This step exists because the guard on their side and the release on this side each see
half of the problem, and the half they cannot see is the one a message covers.

## Never

- **Never delete a release.** Deleting one is what left Zenodo returning `409` with no DOI. It is not undoable by
  retrying.
- **Never edit a published deposit** to fix something. Publish the next version; the point of an archive is that
  the cited object does not move.
- **Never edit the preregistration in `PROTOCOL.md`.** Corrections are dated addenda, and a release is how they
  become citable.
