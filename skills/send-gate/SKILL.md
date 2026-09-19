---
name: send-gate
description: Gate every outbound email/SMS/DM/post through hash-dedupe, per-recipient daily caps, a link-200 check and a freeze switch before any send. Use before ANY message leaves the machine.
---

# send-gate

Autonomous agents fail loudly in one specific way: **they send the same thing twice, or ten times.**
A cron that fires daily instead of weekly, a retry loop on an SMTP error, a skill that
forgot to check yesterday's log. send-gate is a small, dependency-free Python module that
sits in front of every send.

## Three hard rules (no exceptions)

1. **HASH DEDUPE** — `sha256(recipient + subject + body)`; an identical hash within 24 h is BLOCKED.
2. **DAILY CAP** — max **2** messages per external recipient per day per agent (configurable, never unlimited).
3. **SEND-ERROR = STOP** — any provider error is logged and the run stops. NEVER auto-retry a send.

Plus two guards:

4. **LINK-200** — every URL in the body is fetched in its exact form within 5 minutes of sending and must return 200 (a 3xx that lands on 200 is fine; anything else = FAIL, do not send).
5. **FREEZE SWITCH** — `~/.geai-brain/freeze.json` `{"frozen": true}` blocks everything until a human flips it back.

## Use

```python
import sys; sys.path.insert(0, "~/.geai-brain/skills/send-gate".replace("~", __import__("os").path.expanduser("~")))
from send_gate import check_send, record_send

ok, reason = check_send(recipient="jane@example.com", subject="Hi", body="Details: https://example.com/p", agent="outreach")
if not ok:
    print("BLOCKED:", reason); raise SystemExit(0)
# ... your provider send here ... (any exception -> log + stop, no retry)
record_send(recipient="jane@example.com", subject="Hi", body="...", agent="outreach", provider_id="<Message-ID>")
```

CLI dry-check:

```bash
python3 ~/.geai-brain/skills/send-gate/send_gate.py check jane@example.com "Subject" "Body with https://example.com" outreach
python3 ~/.geai-brain/skills/send-gate/send_gate.py stats
```

## State

`~/.geai-brain/send_gate.json` — `{"sends": [{ts, agent, recipient, hash, provider_id}], "cap_per_recipient_per_day": 2}`.
Human-readable, git-friendly, no database.

## Quiet hours

Client-facing sends are refused between **19:00 and 08:00** local time unless `quiet_ok=True` is passed
(operational alerts to the owner are exempt — pass `internal=True`).

## What this is not

It is not a mailer. It never holds credentials. It only answers *"may this go out right now?"* and remembers what went out.
