#!/usr/bin/env python3
"""scoreboard — reach / replies / demos / paid / $spent / $in from events.db. n/a when no record. (GEAI Brain Lite, MIT)"""
import argparse
import json
import os
import sqlite3
from datetime import datetime, timedelta

STATE_DIR = os.environ.get("GEAI_BRAIN_HOME", os.path.expanduser("~/.geai-brain"))
DB_PATH = os.path.join(STATE_DIR, "events.db")
COLS = {
    "reach": ("post", "email_sent", "sms_sent", "dm_sent", "letter_sent"),
    "replies": ("reply",),
    "demos": ("demo_booked", "demo_done"),
    "paid": ("payment",),
}


def window(week):
    now = datetime.now()
    if week:
        start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, now


def board(week=False, project=None, zero=False):
    start, now = window(week)
    out = {"window": f"{start:%Y-%m-%d %H:%M} .. {now:%Y-%m-%d %H:%M}", "project": project or "all", "source": DB_PATH}
    if not os.path.exists(DB_PATH):
        for c in list(COLS) + ["$spent", "$in"]:
            out[c] = "n/a"
        out["note"] = "no events.db yet"
        return out
    conn = sqlite3.connect(DB_PATH)
    where = "ts >= ?" + (" AND project = ?" if project else "")
    args = [start.isoformat()] + ([project] if project else [])
    for col, types in COLS.items():
        q = f"SELECT COUNT(*) FROM events WHERE {where} AND event_type IN ({','.join('?' * len(types))})"
        n = conn.execute(q, args + list(types)).fetchone()[0]
        out[col] = n if (n or zero) else "n/a"
    spent = conn.execute(f"SELECT COALESCE(SUM(cost),0), COUNT(*) FROM events WHERE {where} AND event_type != 'payment'", args).fetchone()
    inc = conn.execute(f"SELECT COALESCE(SUM(cost),0), COUNT(*) FROM events WHERE {where} AND event_type = 'payment'", args).fetchone()
    out["$spent"] = round(spent[0], 2) if (spent[1] or zero) else "n/a"
    out["$in"] = round(inc[0], 2) if (inc[1] or zero) else "n/a"
    conn.close()
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--week", action="store_true"); p.add_argument("--project"); p.add_argument("--json", action="store_true")
    p.add_argument("--zero", action="store_true", help="print 0 instead of n/a when a type has no rows")
    a = p.parse_args()
    b = board(a.week, a.project, a.zero)
    if a.json:
        print(json.dumps(b, indent=1))
    else:
        print(f"SCOREBOARD {b['window']} [{b['project']}]")
        print(" · ".join(f"{k} {b[k]}" for k in ("reach", "replies", "demos", "paid", "$spent", "$in")))
        if "note" in b:
            print(b["note"])
