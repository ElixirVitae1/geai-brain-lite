#!/usr/bin/env bash
# GEAI Brain Lite installer (MIT) — https://github.com/ElixirVitae1/geai-brain-lite
# Installs 3 skills (verify-on-claim, send-gate, truth-scoreboard) for Claude Code, OpenClaw and Hermes agents.
# $0, no accounts, no network beyond cloning this repo. Idempotent. Prints its own VERIFIED-BY artifact.
set -euo pipefail

BRAIN_HOME="${GEAI_BRAIN_HOME:-$HOME/.geai-brain}"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS=(verify-on-claim send-gate truth-scoreboard)
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

log() { printf '[geai-brain-lite] %s\n' "$*"; }

command -v python3 >/dev/null 2>&1 || { log "python3 is required (stdlib only, no pip)"; exit 1; }

# 1. canonical copy under ~/.geai-brain
mkdir -p "$BRAIN_HOME/skills"
for s in "${SKILLS[@]}"; do
  rm -rf "$BRAIN_HOME/skills/$s"
  cp -R "$SRC_DIR/skills/$s" "$BRAIN_HOME/skills/$s"
done
cp "$SRC_DIR/RULES.md" "$BRAIN_HOME/RULES.md"
chmod +x "$BRAIN_HOME"/skills/*/*.sh "$BRAIN_HOME"/skills/*/*.py 2>/dev/null || true
[ -f "$BRAIN_HOME/freeze.json" ] || printf '{"frozen": false}\n' > "$BRAIN_HOME/freeze.json"

# 2. init the event log
python3 "$BRAIN_HOME/skills/truth-scoreboard/events.py" log geai-brain install installed --ref "$ts" --raw "$BRAIN_HOME" >/dev/null

# 3. link skills into every agent runtime we can find
linked=()
link_into() {  # $1 = skills dir of an agent runtime
  mkdir -p "$1"
  for s in "${SKILLS[@]}"; do
    rm -rf "$1/$s"
    ln -s "$BRAIN_HOME/skills/$s" "$1/$s" 2>/dev/null || cp -R "$BRAIN_HOME/skills/$s" "$1/$s"
  done
  linked+=("$1")
}
# Claude Code (user-level skills), always
link_into "$HOME/.claude/skills"
# OpenClaw / Clawdbot / Hermes: only if the runtime dir already exists
for d in "$HOME/.openclaw" "$HOME/.clawdbot" "$HOME/.hermes"; do
  [ -d "$d" ] && link_into "$d/skills"
done
# project-level: if run inside a repo with a .claude dir, link there too
if [ -d "$PWD/.claude" ] && [ "$PWD" != "$HOME" ]; then link_into "$PWD/.claude/skills"; fi

# 4. append the rules block to the user CLAUDE.md once (marker-guarded)
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
MARK="<!-- geai-brain-lite rules v1 -->"
mkdir -p "$HOME/.claude"
if ! grep -qF "$MARK" "$CLAUDE_MD" 2>/dev/null; then
  { printf '\n%s\n' "$MARK"; cat "$SRC_DIR/RULES.md"; printf '%s\n' "<!-- /geai-brain-lite -->"; } >> "$CLAUDE_MD"
  log "rules appended to $CLAUDE_MD"
else
  log "rules already present in $CLAUDE_MD (skipped)"
fi

# 5. self-test: run each skill once, dry
python3 "$BRAIN_HOME/skills/send-gate/send_gate.py" stats >/dev/null
python3 "$BRAIN_HOME/skills/truth-scoreboard/scoreboard.py" >/dev/null
bash "$BRAIN_HOME/skills/verify-on-claim/verify.sh" file "$BRAIN_HOME/RULES.md" >/dev/null

# 6. artifact
log "installed to $BRAIN_HOME @ $ts"
for d in "${linked[@]}"; do log "skills linked: $d"; done
echo "VERIFIED-BY: $(find "$BRAIN_HOME/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d " ") skill dirs in $BRAIN_HOME/skills; $(python3 "$BRAIN_HOME/skills/truth-scoreboard/events.py" tail -n 1)"
