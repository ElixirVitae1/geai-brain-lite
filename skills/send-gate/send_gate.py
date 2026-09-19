#!/usr/bin/env python3
"""send_gate — may this message go out right now?  (GEAI Brain Lite, MIT)

Rules: 24h hash dedupe · per-recipient daily cap · link-200 check · freeze switch · quiet hours.
No credentials, no provider code. Stdlib only.
"""
import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta

HOME = os.path.expanduser("~")
STATE_DIR = os.environ.get("GEAI_BRAIN_HOME", os.path.join(HOME, ".geai-brain"))
STATE = os.path.join(STATE_DIR, "send_gate.json")
FREEZE = os.path.join(STATE_DIR, "freeze.json")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")
QUIET_START, QUIET_END = 19, 8  # local hours


def _load():
    if not os.path.exists(STATE):
        return {"sends": [], "cap_per_recipient_per_day": 2}
    with open(STATE) as f:
        return json.load(f)


def _save(s):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f, indent=1)
    os.replace(tmp, STATE)


def _hash(recipient, subject, body):
    return hashlib.sha256(f"{recipient}\n{subject}\n{body}".encode()).hexdigest()


def frozen():
    try:
        with open(FREEZE) as f:
            return bool(json.load(f).get("frozen"))
    except FileNotFoundError:
        return False


def link_check(body, timeout=15):
    """Return (ok, [(url, code)]). Every URL must land on 200."""
    results = []
    for url in URL_RE.findall(body or ""):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "geai-brain-lite/send-gate"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                results.append((url, r.status))
        except Exception as e:  # noqa: BLE001
            code = getattr(e, "code", None) or f"ERR {type(e).__name__}"
            results.append((url, code))
    return all(c == 200 for _, c in results), results


def check_send(recipient, subject, body, agent, internal=False, quiet_ok=False, check_links=True):
    """Return (True, 'ok') or (False, reason). Does NOT record — call record_send after the provider confirms."""
    if frozen():
        return False, "FROZEN: ~/.geai-brain/freeze.json frozen=true"
    now = datetime.now()
    if not internal and not quiet_ok and (now.hour >= QUIET_START or now.hour < QUIET_END):
        return False, f"QUIET-HOURS: {now:%H:%M} local is inside {QUIET_START}:00-{QUIET_END:02d}:00"
    s = _load()
    h = _hash(recipient, subject, body)
    day_ago = (now - timedelta(hours=24)).isoformat()
    today = now.date().isoformat()
    for e in s["sends"]:
        if e["hash"] == h and e["ts"] >= day_ago:
            return False, f"DEDUPE: identical message to {recipient} at {e['ts']}"
    n_today = sum(1 for e in s["sends"] if e["recipient"] == recipient and e["agent"] == agent and e["ts"][:10] == today)
    cap = int(s.get("cap_per_recipient_per_day", 2))
    if not internal and n_today >= cap:
        return False, f"DAILY-CAP: {n_today}/{cap} already sent to {recipient} by {agent} today"
    if check_links:
        ok, res = link_check(body)
        if not ok:
            return False, "LINK-FAIL: " + ", ".join(f"{u} -> {c}" for u, c in res)
    return True, "ok"


def record_send(recipient, subject, body, agent, provider_id=""):
    s = _load()
    s["sends"].append({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "agent": agent, "recipient": recipient,
        "hash": _hash(recipient, subject, body), "provider_id": str(provider_id)[:120],
    })
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    s["sends"] = [e for e in s["sends"] if e["ts"] >= cutoff]
    _save(s)
    return s["sends"][-1]


def stats():
    s = _load()
    today = datetime.now().date().isoformat()
    by_agent = {}
    for e in s["sends"]:
        if e["ts"][:10] == today:
            by_agent[e["agent"]] = by_agent.get(e["agent"], 0) + 1
    return {"today": by_agent, "total_30d": len(s["sends"]), "frozen": frozen(), "cap": s.get("cap_per_recipient_per_day", 2)}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["check"] and len(a) >= 5:
        ok, why = check_send(a[1], a[2], a[3], a[4], quiet_ok="--quiet-ok" in a)
        print("ALLOW" if ok else "BLOCK", why)
        sys.exit(0 if ok else 1)
    if a[:1] == ["record"] and len(a) >= 5:
        print(json.dumps(record_send(a[1], a[2], a[3], a[4], a[5] if len(a) > 5 else "")))
        sys.exit(0)
    if a[:1] == ["stats"]:
        print(json.dumps(stats(), indent=1)); sys.exit(0)
    if a[:1] == ["freeze"]:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(FREEZE, "w") as f:
            json.dump({"frozen": a[1:2] != ["off"], "ts": datetime.now().isoformat(timespec="seconds")}, f)
        print("frozen =", frozen()); sys.exit(0)
    print("usage: send_gate.py check <to> <subject> <body> <agent> [--quiet-ok] | record <to> <subject> <body> <agent> [provider_id] | stats | freeze [off]")
    sys.exit(2)
