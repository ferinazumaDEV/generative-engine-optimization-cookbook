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
import json, os, sys

# Canonical list of answer-engine crawler user-agents we test for.
AI_AGENTS = [
    "GPTBot", "ClaudeBot", "anthropic-ai", "PerplexityBot",
    "Google-Extended", "CCBot", "Applebot-Extended", "Bytespider",
]

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

    def allowed(agent):
        """Is `agent` allowed to fetch path '/' ? Most-specific group wins
        (exact user-agent match, else '*'); within it, the longest matching
        rule wins and Allow breaks ties, per the robots.txt convention."""
        a = agent.lower()
        rules = groups.get(a, groups.get("*"))
        if rules is None:                 # no group applies -> default allow
            return True
        best_len, best_allow = -1, True   # default allow if no rule matches '/'
        for directive, value in rules:
            if value == "":
                # empty Disallow == "allow everything"; empty Allow is a no-op
                if directive != "disallow":
                    continue
                length, is_allow = 0, True
            else:
                if not "/".startswith(value):
                    continue
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
             "metric": "AI crawler user-agents allowed by robots.txt for path / (of the 8 tested)",
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
  echo "before: AI crawlers blocked in robots.txt and no /llms.txt -> nothing to cite."
  echo "after:  AI crawlers allowed and a curated /llms.txt published -> extractable."
fi
