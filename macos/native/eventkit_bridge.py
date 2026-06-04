#!/usr/bin/env python3
"""Native Apple Calendar + Reminders bridge via osascript (AppleScript).

Lets the harness read/write the user's real Apple Calendar and Reminders instead of routing
everything through Feishu calendar. osascript needs no Swift/pyobjc and is present on every Mac
(the app will prompt once for Automation permission). All commands are no-ops off macOS.

Usage:
  python3 eventkit_bridge.py agenda [--days 1]          # today's events as JSON
  python3 eventkit_bridge.py reminders                  # open reminders as JSON
  python3 eventkit_bridge.py remind "title" [--due "2026-06-05 09:00"] [--list Inbox]
  python3 eventkit_bridge.py event "title" --start "2026-06-05 14:00" --end "2026-06-05 15:00"
"""
import argparse, json, subprocess, sys


def osa(script):
    if sys.platform != "darwin":
        raise RuntimeError("eventkit_bridge uses AppleScript — run on macOS")
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "osascript failed")
    return r.stdout.strip()


def agenda(days):
    # returns "title|start|end" lines for events between now and now+days
    script = f'''
    set output to ""
    set theStart to current date
    set theEnd to theStart + ({days} * days)
    tell application "Calendar"
      repeat with c in calendars
        repeat with e in (every event of c whose start date is greater than theStart and start date is less than theEnd)
          set output to output & (summary of e) & "|" & (start date of e as string) & "|" & (end date of e as string) & linefeed
        end repeat
      end repeat
    end tell
    return output'''
    out = osa(script)
    items = []
    for line in out.splitlines():
        if "|" in line:
            t, s, e = (line.split("|") + ["", ""])[:3]
            items.append({"title": t, "start": s, "end": e})
    return items


def reminders():
    script = '''
    set output to ""
    tell application "Reminders"
      repeat with r in (every reminder whose completed is false)
        set d to ""
        try
          set d to (due date of r as string)
        end try
        set output to output & (name of r) & "|" & d & linefeed
      end repeat
    end tell
    return output'''
    out = osa(script)
    items = []
    for line in out.splitlines():
        if "|" in line:
            n, d = (line.split("|") + [""])[:2]
            items.append({"title": n, "due": d})
    return items


def add_reminder(title, due, listname):
    due_clause = f'set due date of newR to date "{due}"' if due else ""
    list_clause = f'tell list "{listname}"' if listname else "tell default list"
    script = f'''
    tell application "Reminders"
      {list_clause}
        set newR to make new reminder with properties {{name:"{title}"}}
        {due_clause}
      end tell
    end tell
    return "ok"'''
    return osa(script)


def add_event(title, start, end, cal):
    cal_clause = f'calendar "{cal}"' if cal else "calendar 1"
    script = f'''
    tell application "Calendar"
      tell {cal_clause}
        make new event with properties {{summary:"{title}", start date:date "{start}", end date:date "{end}"}}
      end tell
    end tell
    return "ok"'''
    return osa(script)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("agenda"); a1.add_argument("--days", type=int, default=1)
    sub.add_parser("reminders")
    r = sub.add_parser("remind"); r.add_argument("title"); r.add_argument("--due", default=""); r.add_argument("--list", default="")
    e = sub.add_parser("event"); e.add_argument("title"); e.add_argument("--start", required=True); e.add_argument("--end", required=True); e.add_argument("--cal", default="")
    a = ap.parse_args()
    if a.cmd == "agenda":
        print(json.dumps(agenda(a.days), ensure_ascii=False))
    elif a.cmd == "reminders":
        print(json.dumps(reminders(), ensure_ascii=False))
    elif a.cmd == "remind":
        print(add_reminder(a.title, a.due, a.list))
    elif a.cmd == "event":
        print(add_event(a.title, a.start, a.end, a.cal))
    return 0


if __name__ == "__main__":
    sys.exit(main())
