#!/usr/bin/env python3
"""events — one append-only event log for every agent (GEAI Brain Lite, MIT). Stdlib only."""
import argparse
import os
import sqlite3
from datetime import datetime

STATE_DIR = os.environ.get("GEAI_BRAIN_HOME", os.path.expanduser("~/.geai-brain"))
DB_PATH = os.path.join(STATE_DIR, "events.db")
SCHEMA = ("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, project TEXT, "
          "source TEXT, event_type TEXT NOT NULL, actor TEXT, cost REAL DEFAULT 0, outcome TEXT, ref_id TEXT, raw_path TEXT)")


def connect():
    os.makedirs(STATE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_events_ts ON events(ts)")
    return conn


def log_event(project, source, event_type, actor="", cost=0.0, outcome="", ref_id="", raw_path=""):
    """Append one event. Returns the row id."""
    conn = connect()
    cur = conn.execute(
        "INSERT INTO events (ts, project, source, event_type, actor, cost, outcome, ref_id, raw_path) VALUES (?,?,?,?,?,?,?,?,?)",
        (datetime.now().astimezone().isoformat(timespec="seconds"), project, source, event_type,
         str(actor)[:200], float(cost or 0), str(outcome)[:500], str(ref_id)[:120], str(raw_path)[:300]))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("log")
    l.add_argument("project"); l.add_argument("source"); l.add_argument("event_type")
    l.add_argument("--actor", default=""); l.add_argument("--cost", type=float, default=0.0)
    l.add_argument("--outcome", default=""); l.add_argument("--ref", default=""); l.add_argument("--raw", default="")
    sub.add_parser("path")
    t = sub.add_parser("tail"); t.add_argument("-n", type=int, default=10)
    a = p.parse_args()
    if a.cmd == "log":
        print("event id", log_event(a.project, a.source, a.event_type, a.actor, a.cost, a.outcome, a.ref, a.raw))
    elif a.cmd == "path":
        print(DB_PATH)
    else:
        conn = connect()
        for row in conn.execute("SELECT id, ts, project, source, event_type, cost, outcome, ref_id FROM events ORDER BY id DESC LIMIT ?", (a.n,)):
            print(*row, sep=" | ")
