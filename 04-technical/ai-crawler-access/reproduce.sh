#!/usr/bin/env bash
# Can AI answer engines fetch this site, and is there a curated feed for them?
# Two deterministic proxies, measured offline (no network, no browser, no LLM):
#   1) how many known AI crawler user-agents are ALLOWED by robots.txt
#   2) how many bytes of curated, machine-readable content /llms.txt exposes
# Run over before/ (blocked, no feed) and after/ (allowed + llms.txt).
#
# Usage: bash reproduce.sh [--json]
#   (no flag)  human-readable table, unchanged
#   --json     the same numbers as JSON on stdout, for dataset/build.sh
set -euo pipefail
cd "$(dirname "$0")"

JSON=0
for arg in "$@"; do
  [ "$arg" = "--json" ] && JSON=1
done

python3 - "$@" <<'PY'
import json, os, re, sys

# The tokens this recipe evaluates, grouped by what they actually control.
# They are NOT all HTTP crawlers, and the difference matters when reading the
# number: allowing every one of them is a statement of policy across four
# different mechanisms, not "eight robots can now fetch the page".
#
#   retrieval  a crawler that fetches pages for a search or answer index
#   training   a crawler that fetches pages to train models
#   usage      a policy token with NO independent HTTP user-agent; it governs
#              how already-fetched content may be used
#   broad      a general web crawler whose corpus is widely reused
#
# Sources are each vendor's own documentation, checked 2026-09-12.
AGENT_ROLES = [
    ("GPTBot",            "training",  "https://developers.openai.com/api/docs/bots"),
    ("ClaudeBot",         "training",  "https://support.anthropic.com/en/articles/8896518"),
    ("anthropic-ai",      "training",  "https://support.anthropic.com/en/articles/8896518"),
    ("PerplexityBot",     "retrieval", "https://docs.perplexity.ai/guides/bots"),
    ("Google-Extended",   "usage",     "https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers"),
    ("CCBot",             "broad",     "https://commoncrawl.org/ccbot"),
    ("Applebot-Extended", "usage",     "https://support.apple.com/en-us/119829"),
    ("Bytespider",        "training",  "https://www.bytedance.com/en/"),
]
AI_AGENTS = [name for name, _role, _src in AGENT_ROLES]

# Deliberately NOT added here: OAI-SearchBot, the retrieval counterpart of
# GPTBot. It belongs in a roster that claims to cover answer engines, but adding
# it changes the measured value from 8 to 9 and would make this release's number
# incomparable with the one already published and archived. Changing the roster
# is a dataset decision -- a new schema_version -- not a bug fix, and it is
# tracked separately from this correction.

def measure(variant):
    robots_path = os.path.join(variant, "robots.txt")
    llms_path   = os.path.join(variant, "llms.txt")

    # --- Parse robots.txt into groups: {user-agent(lower): [(directive, value), ...]} ---
    groups = {}
    current_agents = []
    starting_group = False
    if os.path.exists(robots_path):
        with open(robots_path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.split("#", 1)[0].strip()
                if not line or ":" not in line:
                    continue
                field, _, value = line.partition(":")
                field = field.strip().lower()
                value = value.strip()
                if field == "user-agent":
                    if not starting_group:
                        current_agents = []
                    current_agents.append(value.lower())
                    groups.setdefault(value.lower(), [])
                    starting_group = True
                elif field in ("allow", "disallow"):
                    starting_group = False
                    for a in current_agents:
                        groups[a].append((field, value))

    def _pattern_matches(pattern, path):
        """Does an RFC 9309 path pattern match `path`?

        The first version of this compared with str.startswith, which treats the
        two special characters of the grammar as ordinary text. `Disallow: /*`
        therefore matched nothing and the measurement reported the path as
        ALLOWED -- a false positive on a rule that blocks the whole site, which
        is the single most common way to say "stay out".

        RFC 9309 section 2.2.2 defines exactly two: `*` matches any sequence of
        characters, and `$` at the end of the pattern anchors the match to the
        end of the path. Everything else is literal.
        """
        anchored = pattern.endswith("$")
        body = pattern[:-1] if anchored else pattern
        expr = "".join(".*" if ch == "*" else re.escape(ch) for ch in body)
        return re.match(expr + ("$" if anchored else ""), path) is not None

    def allowed(agent, path="/"):
        """Is `agent` allowed to fetch `path`?

        Most-specific group wins (exact user-agent match, else `*`); within it
        the longest matching rule wins and Allow breaks a tie of equal length,
        per RFC 9309 section 2.2.2. An empty Disallow means "allow everything";
        an empty Allow is a no-op.
        """
        a = agent.lower()
        rules = groups.get(a, groups.get("*"))
        if rules is None:                 # no group applies -> default allow
            return True
        best_len, best_allow = -1, True   # default allow if no rule matches
        for directive, value in rules:
            if value == "":
                if directive != "disallow":
                    continue
                length, is_allow = 0, True
            else:
                if not _pattern_matches(value, path):
                    continue
                # RFC 9309 compares by the length of the PATTERN, not of the
                # matched text, so /* and / are not the same length.
                length, is_allow = len(value), (directive == "allow")
            if length > best_len or (length == best_len and is_allow):
                best_len, best_allow = length, is_allow
        return best_allow

    allowed_count = sum(1 for ua in AI_AGENTS if allowed(ua))

    # --- llms.txt: bytes of curated content exposed (0 if the file is absent) ---
    llms_bytes = os.path.getsize(llms_path) if os.path.exists(llms_path) else 0

    return allowed_count, llms_bytes

rows = []
for variant, robots_policy, llms_state in (("before", "blocks AI crawlers", "absent"),
                                           ("after", "allows AI crawlers", "present")):
    allowed_count, llms_bytes = measure(variant)
    rows.append({"variant": variant, "robots_policy": robots_policy,
                 "llms_txt": llms_state,
                 "ai_user_agents_allowed": allowed_count,
                 "ai_user_agents_tested": len(AI_AGENTS),
                 "llms_txt_bytes": llms_bytes})

if "--json" in sys.argv[1:]:
    json.dump({
        "technique": "ai-crawler-access",
        "chapter": "04-technical",
        "handbook_section": "docs/04-technical.md",
        "title": "AI crawler access: allow AI crawlers in robots.txt + publish an llms.txt",
        "method": "deterministic-offline",
        "requires_llm": False,
        "requires_network": False,
        "measurements": [
            {"id": "ai_user_agents_allowed", "role": "primary",
             "metric": "AI-related robots.txt tokens allowed for path / (of the 8 tested; a mix of retrieval, training and usage-control tokens, not all of them HTTP crawlers)",
             "unit": "user-agents",
             "before_value": rows[0]["ai_user_agents_allowed"],
             "after_value": rows[1]["ai_user_agents_allowed"]},
            {"id": "llms_txt_bytes", "role": "secondary",
             "metric": "bytes of curated content exposed by llms.txt",
             "unit": "bytes",
             "before_value": rows[0]["llms_txt_bytes"],
             "after_value": rows[1]["llms_txt_bytes"]},
        ],
        "user_agents_tested": AI_AGENTS,
        "table": rows,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0)

print('%-8s %-28s %s' % ("VARIANT", "AI UAs ALLOWED (of 8)", "llms.txt BYTES EXPOSED"))
for r in rows:
    print('%-8s %-28s %s' % (r["variant"], r["ai_user_agents_allowed"], r["llms_txt_bytes"]))
PY

if [ "$JSON" -eq 0 ]; then
  echo
  echo "before: every tested token is disallowed in robots.txt, and no /llms.txt is served."
  echo "        That is a statement of declared access. It does not measure whether any"
  echo "        engine retrieved, indexed or cited the page -- none of which is observed here."
  echo "after:  every tested token is allowed and a curated /llms.txt is served."
  echo "        Still declared access, now permissive. Whether any engine acts on it"
  echo "        is the open question this cookbook does not answer."
fi
