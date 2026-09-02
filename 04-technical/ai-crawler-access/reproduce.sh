#!/usr/bin/env bash
# Can AI answer engines fetch this site, and is there a curated feed for them?
# Two deterministic proxies, measured offline (no network, no browser, no LLM):
#   1) how many known AI crawler user-agents are ALLOWED by robots.txt
#   2) how many bytes of curated, machine-readable content /llms.txt exposes
# Run over before/ (blocked, no feed) and after/ (allowed + llms.txt).
set -euo pipefail
cd "$(dirname "$0")"

measure() {  # $1 = variant dir (before|after)
  python3 - "$1" <<'PY'
import sys, os

# Canonical list of answer-engine crawler user-agents we test for.
AI_AGENTS = [
    "GPTBot", "ClaudeBot", "anthropic-ai", "PerplexityBot",
    "Google-Extended", "CCBot", "Applebot-Extended", "Bytespider",
]

variant = sys.argv[1]
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

print(f"{allowed_count}\t{llms_bytes}")
PY
}

printf '%-8s %-28s %s\n' "VARIANT" "AI UAs ALLOWED (of 8)" "llms.txt BYTES EXPOSED"
for v in before after; do
  read -r allowed_count llms_bytes < <(measure "$v")
  printf '%-8s %-28s %s\n' "$v" "$allowed_count" "$llms_bytes"
done

echo
echo "before: AI crawlers blocked in robots.txt and no /llms.txt -> nothing to cite."
echo "after:  AI crawlers allowed and a curated /llms.txt published -> extractable."
