#!/usr/bin/env python3
"""Check that the built dataset says what this cookbook promises it says.

    python3 dataset/validate.py

`build.sh` already refuses to write a dataset whose numbers disagree with the
recipes' `meta.yml`. This is the second half: it checks the *artifacts* — that
the JSON is well-formed against the schema in SCHEMA.md, that the CSV carries
exactly the same records, and that the derived columns really are derived and
not typed in by hand.

The two files are the thing a third party downloads and cites. Nothing was
checking them.

Standard library only, deliberately: the cookbook has no third-party
dependencies and validating it must not introduce one.

Exit status is 0 when everything holds, 1 otherwise, with every failure listed
rather than only the first — a half-diagnosed dataset costs another round trip.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JSON_PATH = os.path.join(HERE, "geo-offline-measurements.json")
CSV_PATH = os.path.join(HERE, "geo-offline-measurements.csv")

TOP_LEVEL_KEYS = {
    "dataset", "schema_version", "description", "source_repository", "version",
    "doi", "date_modified", "author", "schema_documentation", "regenerate_with",
    "license", "method", "requires_llm", "requires_network",
    "what_this_does_not_show", "recipe_count", "measurement_count", "recipes",
    "measurements",
}

CSV_COLUMNS = [
    "technique", "chapter", "recipe_path", "handbook_section", "title",
    "metric_id", "metric_role", "metric", "unit",
    "before_value", "after_value", "absolute_change", "ratio_after_over_before",
    "method", "requires_llm", "requires_network", "engines", "tool",
    "sample_size", "sample_unit", "confidence",
    "measured_date", "last_verified", "limitations",
]

problems: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        problems.append(message)


def as_csv_value(value: object) -> str:
    """Render a JSON value the way build.sh writes it into the CSV."""
    if value is None:
        return ""                      # an empty cell means "no value", never 0
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ";".join(str(v) for v in value)
    return str(value)


def main() -> int:
    with open(JSON_PATH, encoding="utf-8") as fh:
        doc = json.load(fh)

    # -- structure --------------------------------------------------------- #
    check(set(doc) == TOP_LEVEL_KEYS,
          f"JSON top-level keys differ from the schema: "
          f"missing {sorted(TOP_LEVEL_KEYS - set(doc))}, "
          f"unexpected {sorted(set(doc) - TOP_LEVEL_KEYS)}")
    check(doc.get("schema_version") == 1,
          f"unsupported schema_version {doc.get('schema_version')!r}")

    recipes = doc.get("recipes", [])
    measurements = doc.get("measurements", [])
    check(doc.get("recipe_count") == len(recipes),
          f"recipe_count is {doc.get('recipe_count')} but there are {len(recipes)} recipes")
    check(doc.get("measurement_count") == len(measurements),
          f"measurement_count is {doc.get('measurement_count')} but there are "
          f"{len(measurements)} measurements")
    check(len(recipes) > 0 and len(measurements) > 0,
          "the dataset is empty; build.sh should never write that")

    # -- the recipes it names must exist ----------------------------------- #
    for r in recipes:
        path = r.get("recipe_path", "")
        check(os.path.isdir(os.path.join(ROOT, path)),
              f"recipe_path {path!r} is in the dataset but not in the repository")
        primary = [m for m in r.get("measurements", []) if m.get("role") == "primary"]
        check(len(primary) == 1,
              f"{path}: expected exactly one primary measurement, found {len(primary)}")

    # -- citation scalars agree with CITATION.cff -------------------------- #
    citation = {}
    with open(os.path.join(ROOT, "CITATION.cff"), encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r'^(version|date-released|doi):\s*"?([^"#]+?)"?\s*$', line)
            if m:
                citation[m.group(1)] = m.group(2)
    check(doc.get("version") == citation.get("version"),
          f"version {doc.get('version')!r} does not match CITATION.cff "
          f"{citation.get('version')!r}")
    check(doc.get("doi") == citation.get("doi"),
          f"doi {doc.get('doi')!r} does not match CITATION.cff {citation.get('doi')!r}")
    check(doc.get("date_modified") == citation.get("date-released"),
          f"date_modified {doc.get('date_modified')!r} does not match CITATION.cff "
          f"date-released {citation.get('date-released')!r}")

    # -- derived columns are derived --------------------------------------- #
    # If someone edits the dataset by hand instead of rebuilding, this is where
    # it shows: the arithmetic stops agreeing with the two measured values.
    for m in measurements:
        before, after = m.get("before_value"), m.get("after_value")
        key = f"{m.get('technique')}/{m.get('metric_id')}"
        check(m.get("absolute_change") == after - before,
              f"{key}: absolute_change is {m.get('absolute_change')} but "
              f"after - before is {after - before}")
        expected_ratio = round(after / before, 2) if before else None
        check(m.get("ratio_after_over_before") == expected_ratio,
              f"{key}: ratio_after_over_before is {m.get('ratio_after_over_before')} "
              f"but after / before is {expected_ratio}")
        # A zero denominator must give null, never a number: "no ratio exists"
        # and "the ratio is zero" are different statements.
        if not before:
            check(m.get("ratio_after_over_before") is None,
                  f"{key}: before_value is {before} so the ratio must be null")

    # -- the CSV carries the same records ---------------------------------- #
    with open(CSV_PATH, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
        fh.seek(0)
        header = next(csv.reader(fh))

    check(header == CSV_COLUMNS,
          f"CSV header differs from the schema: got {header}")
    check(len(rows) == len(measurements),
          f"the CSV has {len(rows)} rows but the JSON has {len(measurements)} measurements")

    by_key = {(m.get("technique"), m.get("metric_id")): m for m in measurements}
    check(len(by_key) == len(measurements),
          "two measurements share the same technique and metric_id; they are not addressable")

    for i, row in enumerate(rows, start=2):        # 2 = first data line, with the header at 1
        key = (row["technique"], row["metric_id"])
        m = by_key.get(key)
        if m is None:
            problems.append(f"CSV line {i}: {key} has no matching record in the JSON")
            continue
        for column in CSV_COLUMNS:
            expected = as_csv_value(m.get(column))
            check(row[column] == expected,
                  f"CSV line {i} ({key[0]}/{key[1]}): {column} is {row[column]!r} "
                  f"but the JSON says {expected!r}")

    # -- the disclaimer is present and not empty --------------------------- #
    # This dataset's honesty depends on it: every number is an offline proxy and
    # none of them measures citation by any engine. If it ever disappears the
    # numbers start reading as something they are not.
    disclaimer = doc.get("what_this_does_not_show") or ""
    check("citation" in disclaimer.lower() or "cite" in disclaimer.lower(),
          "what_this_does_not_show no longer says the measurements do not "
          "establish citation by any engine")

    if problems:
        sys.stderr.write(f"\nDataset validation FAILED — {len(problems)} problem(s):\n")
        for p in problems:
            sys.stderr.write(f"  - {p}\n")
        sys.stderr.write("\nRebuild with 'bash dataset/build.sh'; do not edit the "
                         "dataset files by hand.\n")
        return 1

    print(f"dataset OK: {len(recipes)} recipes, {len(measurements)} measurements, "
          f"CSV and JSON agree on every field, derived columns check out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
