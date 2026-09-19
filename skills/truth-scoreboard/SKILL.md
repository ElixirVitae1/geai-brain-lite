---
name: truth-scoreboard
description: Log every agent action as an event and print a daily/weekly scoreboard where every number comes from a real record — "n/a" when missing, never estimated. Use for reports, digests and end-of-day summaries.
---

# truth-scoreboard

Agents love to summarize. Summaries drift into fiction ("~12 leads this week") the moment a source is missing.
truth-scoreboard gives every agent one append-only event log and one report that refuses to guess.

## TRUTH-ONLY rule

Every metric in any report, digest or message must come from a real record (this log, a provider API, a database row).
Missing source → the cell says **`n/a`**. Never estimate, round up, or carry forward yesterday's number.
A violation is a critical failure, not a style issue.

## Log an event

```python
import sys, os; sys.path.insert(0, os.path.expanduser("~/.geai-brain/skills/truth-scoreboard"))
from events import log_event
log_event(project="acme", source="outreach", event_type="email_sent", actor="agent:outreach", cost=0.0, outcome="ok", ref_id="<Message-ID>")
```

CLI:

```bash
python3 ~/.geai-brain/skills/truth-scoreboard/events.py log acme outreach email_sent --ref "<id>" --cost 0.02
python3 ~/.geai-brain/skills/truth-scoreboard/scoreboard.py            # today
python3 ~/.geai-brain/skills/truth-scoreboard/scoreboard.py --week     # Mon..now
python3 ~/.geai-brain/skills/truth-scoreboard/scoreboard.py --json
```

Schema (SQLite, `~/.geai-brain/events.db`): `ts, project, source, event_type, actor, cost, outcome, ref_id, raw_path`.
`raw_path` should point at the raw artifact (log line, JSON response) so any number can be traced back.

## Scoreboard columns

`reach · replies · demos · paid · $spent · $in` — each is a plain count/sum of event_types:

| column | event_type(s) counted |
|---|---|
| reach | `post`, `email_sent`, `sms_sent`, `dm_sent`, `letter_sent` |
| replies | `reply` |
| demos | `demo_booked`, `demo_done` |
| paid | `payment` (count) |
| $spent | Σ `cost` over all rows |
| $in | Σ `cost` over `payment` rows (record revenue as positive cost on `payment`) |

No rows of a type → that column prints `n/a` (not `0`) unless `--zero` is passed, because "no record" and "measured zero" are different facts.

## Suggested cron

```
0 17 * * * python3 $HOME/.geai-brain/skills/truth-scoreboard/scoreboard.py >> $HOME/.geai-brain/scoreboard.log 2>&1  # GEAI-SCOREBOARD
```

## Weekly reflection (manual, 5 minutes)

Every Friday read the `--week` board and write three lines in `~/.geai-brain/reflection.md`:
1. Which number moved and what caused it (cite a ref_id).
2. Which number did not move and the single change for next week.
3. What was claimed without a `VERIFIED-BY` (see the verify-on-claim skill) — and reopen it.
