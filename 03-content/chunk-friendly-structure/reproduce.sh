#!/usr/bin/env bash
# When a RAG pipeline ingests a document, it splits it into fixed-size chunks
# and embeds each one independently. A chunk that starts mid-sentence or ends
# mid-sentence is a poor retrieval unit: on its own it is ambiguous, so it is
# less likely to be retrieved and quoted cleanly by an answer engine.
#
# This script chunks each variant with a standard recursive fixed-size splitter
# (chunk_size=800, no overlap, separators ["\n\n","\n"," ",""] — the langchain
# default order) and counts how many chunks are SELF-CONTAINED: they begin at a
# unit boundary (heading, list item, or a new sentence) AND end at one (terminal
# punctuation or a heading line). No network, no browser, no LLM, no randomness.
set -euo pipefail
cd "$(dirname "$0")"

python3 - "$@" <<'PY'
import re, sys

CHUNK_SIZE = 800
SEPARATORS = ["\n\n", "\n", " ", ""]

def _merge(pieces, sep, size):
    """Greedily pack small pieces back together up to `size`, joined by `sep`."""
    chunks, cur, cur_len = [], [], 0
    slen = len(sep)
    for p in pieces:
        add = len(p) + (slen if cur else 0)
        if cur and cur_len + add > size:
            chunks.append(sep.join(cur))
            cur, cur_len = [], 0
            add = len(p)
        cur.append(p)
        cur_len += add
    if cur:
        chunks.append(sep.join(cur))
    return chunks

def recursive_split(text, separators, size):
    """Standard recursive character text splitter (deterministic)."""
    # pick the highest-priority separator that actually occurs in the text
    sep = separators[-1]
    rest = []
    for i, s in enumerate(separators):
        if s == "":
            sep = s
            rest = []
            break
        if s in text:
            sep = s
            rest = separators[i + 1:]
            break
    splits = text.split(sep) if sep else list(text)

    final, good = [], []
    for s in splits:
        if len(s) <= size:
            good.append(s)
        else:
            if good:
                final += _merge(good, sep, size)
                good = []
            if not rest:
                final.append(s)  # cannot split further -> hard cut stays
            else:
                final += recursive_split(s, rest, size)
    if good:
        final += _merge(good, sep, size)
    return [c for c in final if c.strip()]

STARTERS = ("#", "-", "*", ">")
def starts_clean(chunk):
    t = chunk.lstrip()
    if not t:
        return False
    c = t[0]
    return c in STARTERS or c.isupper() or c.isdigit()

def ends_clean(chunk):
    t = chunk.rstrip()
    if not t:
        return False
    last_line = t.splitlines()[-1].lstrip()
    return t.endswith((".", "!", "?", ":")) or last_line.startswith("#")

def self_contained(chunk):
    return starts_clean(chunk) and ends_clean(chunk)

def measure(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    chunks = recursive_split(text, SEPARATORS, CHUNK_SIZE)
    sc = sum(1 for c in chunks if self_contained(c))
    return len(chunks), sc

print("%-8s %-22s %8s %18s %10s" % ("VARIANT", "STRUCTURE", "CHUNKS", "SELF-CONTAINED", "SHARE"))
for variant, label in (("before", "wall of text"), ("after", "chunk-friendly")):
    total, sc = measure(f"{variant}/article.md")
    share = (sc / total * 100) if total else 0.0
    print("%-8s %-22s %8d %18d %9.1f%%" % (variant, label, total, sc, share))
PY

echo
echo "Both files contain the same prose. Only the after/ version is structured"
echo "with headings, short sections and lists. Self-contained chunks are the ones"
echo "a retriever can use on their own, without a neighbour to complete a sentence."
