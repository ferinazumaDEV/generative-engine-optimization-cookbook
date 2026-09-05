#!/usr/bin/env bash
# Rebuild the offline-measurements dataset from the recipes themselves.
#
#   bash dataset/build.sh
#
# It runs each recipe's `reproduce.sh --json`, cross-checks every number and
# label against that recipe's meta.yml, and writes:
#   dataset/geo-offline-measurements.json
#   dataset/geo-offline-measurements.csv
#
# Deterministic and offline: no network, no browser, no LLM, no timestamps, no
# third-party dependencies (bash + python3 standard library). Running it twice
# on an unchanged tree produces byte-identical files, so a stale dataset shows
# up as a diff. If a recipe's --json output disagrees with its meta.yml, the
# build FAILS instead of silently publishing a number nobody measured.
set -euo pipefail

DATASET_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$DATASET_DIR")"
cd "$REPO_ROOT"

RECIPES=(
  "03-content/chunk-friendly-structure"
  "04-technical/ssr-vs-csr-rendering"
  "04-technical/structured-data-jsonld"
  "04-technical/ai-crawler-access"
  "05-authority/entity-clarity-sameas"
  "06-measurement/citation-anchoring"
)

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

for recipe in "${RECIPES[@]}"; do
  echo "run  $recipe/reproduce.sh --json" >&2
  bash "$recipe/reproduce.sh" --json > "$WORK/$(basename "$recipe").json"
done

python3 - "$WORK" "$DATASET_DIR" "${RECIPES[@]}" <<'PY'
import csv, json, sys, os, re

work, dataset_dir, *recipes = sys.argv[1:]

# --- Citation scalars ---------------------------------------------------------
# version, date-released and doi are read from CITATION.cff with a targeted
# regex on those three scalar lines only (the abstract and the identifiers
# list are nested YAML and are deliberately not parsed). CITATION.cff bumps
# version and date-released together with every git tag, so the dataset carries
# the same version, date and DOI as the release it belongs to. The build fails
# if any of the three is missing rather than emitting a dataset nobody can cite.
CITATION = {}
with open("CITATION.cff", encoding="utf-8") as fh:
    for line in fh:
        m = re.match(r'^(version|date-released|doi):\s*"?([^"#]+?)"?\s*$', line)
        if m:
            CITATION[m.group(1)] = m.group(2)
_missing = [k for k in ("version", "date-released", "doi") if k not in CITATION]
if _missing:
    sys.stderr.write(f"CITATION.cff is missing {_missing}; nothing was written.\n")
    sys.exit(1)
AUTHOR = "Fernando Aporta Franco"

# --- Minimal YAML reader ------------------------------------------------------
# meta.yml is deliberately FLAT (scalars and one-line lists only) so it can be
# read with the standard library alone. See dataset/SCHEMA.md.
def read_meta(path):
    meta = {}
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            if value.startswith("[") and value.endswith("]"):
                meta[key] = [v.strip().strip('"').strip("'")
                             for v in value[1:-1].split(",") if v.strip()]
                continue
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            if value == "null":
                meta[key] = None
            elif value == "true":
                meta[key] = True
            elif value == "false":
                meta[key] = False
            elif value.lstrip("-").isdigit():
                meta[key] = int(value)
            else:
                meta[key] = value
    return meta

REQUIRED_KEYS = [
    "schema_version", "technique", "title", "chapter", "handbook_section",
    "status", "method", "requires_llm", "requires_network", "tool", "engines",
    "metric", "unit", "before_value", "after_value",
    "secondary_metric", "secondary_unit", "secondary_before_value",
    "secondary_after_value", "secondary_role",
    "sample_size", "sample_unit", "confidence",
    "measured_date", "last_verified", "limitations",
]

problems = []

def check(condition, message):
    if not condition:
        problems.append(message)

recipe_records, rows = [], []

for recipe in recipes:
    name = os.path.basename(recipe)
    meta = read_meta(os.path.join(recipe, "meta.yml"))
    with open(os.path.join(work, name + ".json"), encoding="utf-8") as fh:
        run = json.load(fh)

    missing = [k for k in REQUIRED_KEYS if k not in meta]
    check(not missing, f"{recipe}: meta.yml is missing keys {missing}")
    extra = [k for k in meta if k not in REQUIRED_KEYS]
    check(not extra, f"{recipe}: meta.yml has keys outside the schema {extra}")
    check(meta.get("schema_version") == 1,
          f"{recipe}: unsupported schema_version {meta.get('schema_version')!r}")

    # The recipe's own --json must agree with its front-matter, field by field.
    for key in ("technique", "chapter", "handbook_section", "title",
                "method", "requires_llm", "requires_network"):
        check(run.get(key) == meta.get(key),
              f"{recipe}: {key} differs — reproduce.sh --json says {run.get(key)!r}, "
              f"meta.yml says {meta.get(key)!r}")

    measurements = run.get("measurements", [])
    primary = [m for m in measurements if m["role"] == "primary"]
    check(len(primary) == 1, f"{recipe}: expected exactly one primary measurement")
    others = [m for m in measurements if m["role"] != "primary"]
    check(len(others) <= 1, f"{recipe}: at most one secondary measurement is supported")

    if primary:
        p = primary[0]
        for run_key, meta_key in (("metric", "metric"), ("unit", "unit"),
                                  ("before_value", "before_value"),
                                  ("after_value", "after_value")):
            check(p[run_key] == meta.get(meta_key),
                  f"{recipe}: primary {run_key} differs — measured {p[run_key]!r}, "
                  f"meta.yml says {meta.get(meta_key)!r}")

    if others:
        s = others[0]
        for run_key, meta_key in (("metric", "secondary_metric"), ("unit", "secondary_unit"),
                                  ("before_value", "secondary_before_value"),
                                  ("after_value", "secondary_after_value"),
                                  ("role", "secondary_role")):
            check(s[run_key] == meta.get(meta_key),
                  f"{recipe}: secondary {run_key} differs — measured {s[run_key]!r}, "
                  f"meta.yml says {meta.get(meta_key)!r}")
    else:
        for meta_key in ("secondary_metric", "secondary_unit", "secondary_before_value",
                         "secondary_after_value", "secondary_role"):
            check(meta.get(meta_key) is None,
                  f"{recipe}: {meta_key} is set but the recipe reports no secondary measurement")

    for m in measurements:
        before, after = m["before_value"], m["after_value"]
        rows.append({
            "technique": meta["technique"],
            "chapter": meta["chapter"],
            "handbook_section": meta["handbook_section"],
            "title": meta["title"],
            "metric_id": m["id"],
            "metric_role": m["role"],
            "metric": m["metric"],
            "unit": m["unit"],
            "before_value": before,
            "after_value": after,
            # Derived by this script from the two measured values, nothing else.
            "absolute_change": after - before,
            "ratio_after_over_before": (round(after / before, 2) if before else None),
            "method": meta["method"],
            "requires_llm": meta["requires_llm"],
            "requires_network": meta["requires_network"],
            "engines": meta["engines"],
            "tool": meta["tool"],
            "sample_size": meta["sample_size"],
            "sample_unit": meta["sample_unit"],
            "confidence": meta["confidence"],
            "measured_date": meta["measured_date"],
            "last_verified": meta["last_verified"],
            "limitations": meta["limitations"],
            "recipe_path": recipe,
        })

    recipe_records.append({
        "technique": meta["technique"],
        "title": meta["title"],
        "chapter": meta["chapter"],
        "recipe_path": recipe,
        "handbook_section": meta["handbook_section"],
        "status": meta["status"],
        "method": meta["method"],
        "requires_llm": meta["requires_llm"],
        "requires_network": meta["requires_network"],
        "tool": meta["tool"],
        "engines": meta["engines"],
        "sample_size": meta["sample_size"],
        "sample_unit": meta["sample_unit"],
        "confidence": meta["confidence"],
        "measured_date": meta["measured_date"],
        "last_verified": meta["last_verified"],
        "limitations": meta["limitations"],
        "measurements": measurements,
        "variants": run.get("table", []),
    })

if problems:
    sys.stderr.write("\nDataset build FAILED — the recipes and their front-matter disagree:\n")
    for p in problems:
        sys.stderr.write(f"  - {p}\n")
    sys.stderr.write("\nNothing was written. Fix the disagreement; do not edit the "
                     "dataset files by hand.\n")
    sys.exit(1)

DISCLAIMER = (
    "Every value here is an offline, deterministic proxy for machine legibility "
    "measured on a controlled before/after artifact. None of them measures "
    "retrieval, reranking, generation or citation by any answer engine, and none "
    "of them establishes that any engine cites the 'after' variant more often."
)

document = {
    "dataset": "GEO offline measurements",
    "schema_version": 1,
    "description": (
        "Before/after values for six deterministic, offline machine-legibility "
        "measurements, one per recipe of the GEO Cookbook."
    ),
    "source_repository": "https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook",
    "version": CITATION["version"],
    "doi": CITATION["doi"],
    "date_modified": CITATION["date-released"],
    "author": AUTHOR,
    "schema_documentation": "dataset/SCHEMA.md",
    "regenerate_with": "bash dataset/build.sh",
    "license": {"data": "CC-BY-4.0", "code": "MIT"},
    "method": "deterministic-offline",
    "requires_llm": False,
    "requires_network": False,
    "what_this_does_not_show": DISCLAIMER,
    "recipe_count": len(recipe_records),
    "measurement_count": len(rows),
    "recipes": recipe_records,
    "measurements": rows,
}

json_path = os.path.join(dataset_dir, "geo-offline-measurements.json")
with open(json_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(document, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

CSV_COLUMNS = [
    "technique", "chapter", "recipe_path", "handbook_section", "title",
    "metric_id", "metric_role", "metric", "unit",
    "before_value", "after_value", "absolute_change", "ratio_after_over_before",
    "method", "requires_llm", "requires_network", "engines", "tool",
    "sample_size", "sample_unit", "confidence",
    "measured_date", "last_verified", "limitations",
]

csv_path = os.path.join(dataset_dir, "geo-offline-measurements.csv")
with open(csv_path, "w", encoding="utf-8", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        out = {k: row[k] for k in CSV_COLUMNS}
        out["engines"] = ";".join(row["engines"])
        for k, v in list(out.items()):
            if v is None:
                out[k] = ""            # an empty cell means "no real value", never 0
            elif isinstance(v, bool):
                out[k] = "true" if v else "false"
        writer.writerow(out)

sys.stderr.write(f"\nwrote {json_path}\n")
sys.stderr.write(f"wrote {csv_path}\n")
sys.stderr.write(f"{len(recipe_records)} recipes, {len(rows)} measurements, "
                 f"all cross-checked against meta.yml\n")
PY
