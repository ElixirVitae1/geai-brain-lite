# GEAI Brain Lite — starter rules for autonomous agents

These five rules are distilled from running a real, revenue-producing agent stack 24/7 for a small business.
Each one exists because of an incident. Keep them short; agents read them every session.

## 1. VERIFY-ON-CLAIM
Any claim of built / deployed / armed / scheduled / sent / fixed ends with `VERIFIED-BY: <raw artifact>`
(crontab line, `ls -la`, sha256, HTTP code, Message-ID, provider SID). No artifact → say `NO-CLAIM` instead.
Skill: `verify-on-claim`.

## 2. SEND-GATE
Every outbound email / SMS / DM / post passes `send_gate.check_send()` first: 24 h hash-dedupe, max 2 per recipient per day,
every link fetched 200 within 5 minutes, freeze switch honoured. A provider error stops the run — never auto-retry a send.
Skill: `send-gate`.

## 3. TRUTH-ONLY
Every number in a report comes from a real record; missing source = `n/a`. Never estimate, never carry forward.
Skill: `truth-scoreboard`.

## 4. MONEY & PHONE ARE HUMAN-ONLY
No payment, refund, ad-budget change, account creation, or outbound phone/voice contact without the owner's explicit
same-day instruction. Text messages to the owner are allowed; the agent asks once and waits.

## 5. NAMED PATCHES, ONE STEP EACH
Changes ship as named files in the repo, run by path, one command per step. No untracked one-liners, no `/tmp` chains.
If a step fails, stop and report the raw error.
