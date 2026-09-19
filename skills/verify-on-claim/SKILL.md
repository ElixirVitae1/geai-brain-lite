---
name: verify-on-claim
description: Never say "done", "deployed", "armed", "sent" or "scheduled" without a raw artifact that proves it. Use before every completion claim.
---

# verify-on-claim

An agent that says "done" without proof is the #1 way autonomous agents burn trust.
This skill makes every completion claim carry a **raw artifact** a human can re-run.

## The rule

Any claim of *built / deployed / armed / scheduled / sent / fixed* MUST end with one line:

```
VERIFIED-BY: <raw artifact>
```

If you cannot produce the artifact, do not make the claim. Say instead:

```
NO-CLAIM: <what you did> — unverified because <reason>
```

## Artifact table (what counts)

| Claim | Required artifact |
|---|---|
| Cron job armed | `crontab -l \| grep <tag>` output line |
| LaunchAgent / systemd unit loaded | `launchctl list \| grep <label>` or `systemctl is-active <unit>` output |
| File created / patched | `ls -la <path>` (size + mtime) and/or `shasum -a 256 <path>` |
| Endpoint deployed | `curl -s -o /dev/null -w '%{http_code}' <exact URL>` → `200` |
| Email sent | Message-ID from the SMTP/API response |
| SMS / chat message sent | provider message SID / id |
| Test passed | the test runner's final summary line |
| Process running | `ps -o pid,etime,command -p <pid>` or `pm2 ls` row |

A *description* of the artifact is not the artifact. Paste the raw line.

## Procedure

1. Do the work.
2. Run the live check from the table (the check must be a fresh command, not a memory).
3. Paste the check output verbatim under `VERIFIED-BY:`.
4. If the check fails → the task is **not done**. Report `NO-CLAIM` and keep working or stop.

## Helper

`verify.sh` in this folder prints a ready-to-paste `VERIFIED-BY:` block for the common cases:

```bash
bash ~/.geai-brain/skills/verify-on-claim/verify.sh url https://example.com/page
bash ~/.geai-brain/skills/verify-on-claim/verify.sh file /path/to/file
bash ~/.geai-brain/skills/verify-on-claim/verify.sh cron MY-TAG
```

## Anti-patterns (all count as FALSE-DONE)

- "I've scheduled it" with no crontab/launchctl line.
- "The page is live" without an HTTP code fetched in the exact form of the link.
- "Email sent" without a Message-ID.
- A voicemail pickup counted as a completed phone contact.
- Re-using yesterday's artifact for today's claim.
