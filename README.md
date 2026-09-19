# GEAI Brain Lite

**Three skills that stop autonomous agents from lying, double-sending, and guessing.**
MIT. Stdlib-only Python + bash. Installs in 10 seconds into Claude Code, OpenClaw, Clawdbot or Hermes.

```bash
git clone https://github.com/ElixirVitae1/geai-brain-lite.git && bash geai-brain-lite/install.sh
```

2-min demo (terminal cards rendered from the real install log): https://www.youtube.com/watch?v=rkKqZZCaNBM

The installer ends with its own proof line:

```
VERIFIED-BY: 3 skill dirs in /home/you/.geai-brain/skills; 1 | 2026-09-19T08:00:00+00:00 | geai-brain | install | installed | 0.0 |  | ...
```

## What's inside

| Skill | The incident it prevents | What it gives you |
|---|---|---|
| `verify-on-claim` | Agent says "scheduled" — nothing was loaded. | `VERIFIED-BY:` rule + `verify.sh url/file/cron/proc` artifact printer |
| `send-gate` | A cron fired daily instead of weekly; a retry loop sent 10 copies. | `check_send()` — 24 h hash-dedupe, 2/recipient/day cap, link-200, freeze switch, quiet hours |
| `truth-scoreboard` | Weekly report said "~12 leads"; the source was missing. | append-only `events.db` + `reach · replies · demos · paid · $spent · $in` board that prints `n/a`, never a guess |

Plus `RULES.md` — five starter rules appended (once, marker-guarded) to `~/.claude/CLAUDE.md`.

## Why these three

We run a paid AI-receptionist + lead pipeline for a law firm on a Mac mini with Claude Code as the operator.
Every rule here is a scar from a real week: a double-sent client update, a "live" page that 404'd, a report that rounded up.
Lite is the part of the brain that is useful to *anyone* running agents that touch other humans.

## Layout after install

```
~/.geai-brain/
  RULES.md
  freeze.json           {"frozen": false}
  events.db             sqlite, created on first event
  send_gate.json        created on first recorded send
  skills/
    verify-on-claim/    SKILL.md verify.sh
    send-gate/          SKILL.md send_gate.py
    truth-scoreboard/   SKILL.md events.py scoreboard.py
~/.claude/skills/<name> -> symlinks to the above (also ~/.openclaw/skills, ~/.hermes/skills if present)
```

Uninstall: `rm -rf ~/.geai-brain ~/.claude/skills/{verify-on-claim,send-gate,truth-scoreboard}` and delete the marked block in `~/.claude/CLAUDE.md`.

## Test it in Docker (what our CI does)

```bash
docker build -t geai-brain-lite-test -f Dockerfile.test . && docker run --rm geai-brain-lite-test
```

## Pro

The full brain (governed outbound mailer, PII lane, weekly reflection, onboarding wizard, 17:00 owner scoreboard SMS, done-for-you install over SSH) is at
**https://genuineempireai.com/p/geai-brain**.

— GEAI Team · Genuine Empire LLC · hello@genuineempireai.com
