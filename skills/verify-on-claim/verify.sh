#!/usr/bin/env bash
# verify.sh — print a ready-to-paste VERIFIED-BY block. Exit 1 if the check fails.
# usage: verify.sh url <URL> | file <PATH> | cron <TAG> | proc <PID>
set -u
kind="${1:-}"; arg="${2:-}"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
case "$kind" in
  url)
    code="$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 20 "$arg")"
    echo "VERIFIED-BY: curl $arg -> HTTP $code @ $ts"
    [ "$code" = "200" ] || { echo "NO-CLAIM: expected 200, got $code"; exit 1; }
    ;;
  file)
    [ -e "$arg" ] || { echo "NO-CLAIM: $arg does not exist"; exit 1; }
    line="$(ls -la "$arg")"
    if command -v shasum >/dev/null 2>&1; then sha="$(shasum -a 256 "$arg" | cut -c1-64)"; else sha="$(sha256sum "$arg" | cut -c1-64)"; fi
    echo "VERIFIED-BY: $line | sha256 $sha @ $ts"
    ;;
  cron)
    line="$(crontab -l 2>/dev/null | grep -F "$arg" | grep -v '^#' | head -1)"
    [ -n "$line" ] || { echo "NO-CLAIM: no active crontab line tagged $arg"; exit 1; }
    echo "VERIFIED-BY: crontab -l | grep $arg -> $line @ $ts"
    ;;
  proc)
    line="$(ps -o pid,etime,command -p "$arg" 2>/dev/null | tail -n +2)"
    [ -n "$line" ] || { echo "NO-CLAIM: pid $arg not running"; exit 1; }
    echo "VERIFIED-BY: ps -p $arg -> $line @ $ts"
    ;;
  *)
    echo "usage: verify.sh url <URL> | file <PATH> | cron <TAG> | proc <PID>"; exit 2 ;;
esac
