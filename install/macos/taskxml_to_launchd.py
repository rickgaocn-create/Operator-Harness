#!/usr/bin/env python3
"""Translate the repo's Windows Task Scheduler XMLs into macOS launchd plists.

The operator-harness ships 38 scheduled jobs as Task Scheduler XML (runtime/scheduled-tasks/).
The routines/daemons they invoke are already portable (Python / Node), so the ONLY thing missing
on macOS is the scheduler binding. This generator reads each XML, extracts the trigger + action,
and emits an equivalent `~/Library/LaunchAgents/com.operator-harness.<name>.plist`.

Trigger mapping:
  ScheduleByDay  (HH:MM)            -> StartCalendarInterval {Hour, Minute}
  ScheduleByWeek (DOW + HH:MM)      -> StartCalendarInterval {Weekday, Hour, Minute}
  Repetition/Interval (PTnH/M/S)    -> StartInterval (seconds)
  LogonTrigger / BootTrigger        -> RunAtLoad + KeepAlive (long-running daemon)

Action mapping:
  Command={{PYTHON_EXE}}            -> ProgramArguments [python3, <script.py>, args...]
  Command=powershell.exe + .ps1     -> the mac bash launcher for that daemon (see DAEMON_MAP)

Usage:
  python3 taskxml_to_launchd.py --tasks-dir <repo>/runtime/scheduled-tasks \
      --out-dir ~/Library/LaunchAgents \
      --python /opt/homebrew/bin/python3 --vault-root ~/Documents/RG --user-home ~
"""
import argparse, os, re, sys, plistlib, xml.etree.ElementTree as ET

NS = "{http://schemas.microsoft.com/windows/2004/02/mit/task}"
LABEL_PREFIX = "com.operator-harness."

# Windows DOW element name -> launchd Weekday number (0/7=Sun .. 6=Sat)
DOW = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3,
       "Thursday": 4, "Friday": 5, "Saturday": 6}

# launchd-native upgrades: tasks better expressed as event-driven WatchPaths than as polling
# daemons. The Windows FileSystemWatcher (clippings) becomes a real WatchPaths trigger that fires
# only on change and writes a signal the session hooks drain.
WATCHPATHS_OVERRIDE = {
    "RG-watcher-clippings": {
        "watch": ["{VAULT_ROOT}/00 Raw/Clippings", "{VAULT_ROOT}/02 Cards/_inbox"],
        "program": ["/bin/bash", "{USER_HOME}/.claude/macos/launchd-native/on-clippings-change.sh"],
    },
}

# powershell daemon tasks -> their mac bash launcher (installed by bootstrap.sh under USER_HOME)
DAEMON_MAP = {
    "afk-code-claude2-daemon":            "{USER_HOME}/.afk-code-claude2/launch-daemon.sh",
    "afk-code-claude2-healthcheck":       "{USER_HOME}/.afk-code-claude2/healthcheck.sh",
    "afk-code-daemon":                    "{USER_HOME}/.afk-code/launch-daemon.sh",
    "feishu-event-consumer-daemon":       "{USER_HOME}/.claude/channels/feishu/launch-consumer.sh",
    "feishu-event-consumer-daemon-personal": "{USER_HOME}/.claude/channels/feishu/launch-consumer-personal.sh",
    "feishu-reader-daemon":               "{USER_HOME}/.claude/channels/feishu/launch-reader.sh",
    "feishu-reader-healthcheck":          "{USER_HOME}/.claude/channels/feishu/reader-healthcheck.sh",
    "fs-claude-daemon":                   "{USER_HOME}/.fs-claude-daemon/launch-fs-daemon.sh",
}


def strip(tag):
    return tag.replace(NS, "")


def find(el, *path):
    cur = el
    for p in path:
        if cur is None:
            return None
        cur = cur.find(NS + p)
    return cur


def iso_hh_mm(boundary):
    """'2026-05-26T23:30:00+08:00' -> (23, 30)."""
    m = re.search(r"T(\d{2}):(\d{2})", boundary or "")
    return (int(m.group(1)), int(m.group(2))) if m else (9, 0)


def duration_to_seconds(s):
    """ISO8601 duration PT3H / PT10M / PT30S / P1D -> seconds."""
    if not s:
        return None
    total = 0
    m = re.match(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", s)
    if not m:
        return None
    d, h, mi, se = (int(x) if x else 0 for x in m.groups())
    total = d * 86400 + h * 3600 + mi * 60 + se
    return total or None


def winpath_to_mac(arg, vault_root, user_home):
    """Convert a Windows arg/path to mac: substitute placeholders, backslash->slash, strip quotes."""
    arg = (arg or "").replace("{{VAULT_ROOT}}", vault_root).replace("{{USER_HOME}}", user_home)
    arg = arg.replace("\\", "/").strip().strip('"')
    return arg


def build_program_args(task_name, exec_el, python, vault_root, user_home):
    cmd = (find(exec_el, "Command").text if find(exec_el, "Command") is not None else "") or ""
    args_el = find(exec_el, "Arguments")
    args_raw = (args_el.text if args_el is not None else "") or ""
    cmd_l = cmd.lower()
    if "{{python_exe}}" in cmd_l or cmd_l.endswith("python.exe") or "python" in cmd_l:
        # python routine: split args, convert each path
        parts = re.findall(r'"[^"]*"|\S+', args_raw)
        prog = [python] + [winpath_to_mac(p, vault_root, user_home) for p in parts]
        return prog
    if "powershell" in cmd_l:
        # daemon launcher -> mac bash equivalent
        launcher = DAEMON_MAP.get(task_name)
        if launcher:
            return ["/bin/bash", launcher.format(USER_HOME=user_home)]
        # generic .ps1 -> try pwsh if available, else skip
        m = re.search(r'-File\s+"?([^"]+\.ps1)"?', args_raw)
        if m:
            return ["/usr/bin/env", "pwsh", "-NoProfile", "-File",
                    winpath_to_mac(m.group(1), vault_root, user_home)]
    # fallback: raw command
    return [winpath_to_mac(cmd, vault_root, user_home)] + \
           [winpath_to_mac(p, vault_root, user_home) for p in re.findall(r'"[^"]*"|\S+', args_raw)]


def _parse_xml(path):
    """Robust parse: schtasks exports are UTF-8/UTF-16 with a (sometimes false) encoding
    declaration that expat rejects. Decode by BOM, then strip the encoding attr before parsing."""
    raw = open(path, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    elif raw[:3] == b"\xef\xbb\xbf":
        text = raw.decode("utf-8-sig")
    else:
        text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<\?xml[^>]*\?>", '<?xml version="1.0"?>', text, count=1)
    return ET.fromstring(text)


def convert(xml_path, python, vault_root, user_home):
    root = _parse_xml(xml_path)
    triggers = find(root, "Triggers")
    actions = find(root, "Actions")
    exec_el = actions.find(NS + "Exec") if actions is not None else None
    if exec_el is None:
        return None  # nothing to run
    name = os.path.splitext(os.path.basename(xml_path))[0]
    label = LABEL_PREFIX + name

    # launchd-native WatchPaths override (event-driven file trigger, no polling)
    if name in WATCHPATHS_OVERRIDE:
        ov = WATCHPATHS_OVERRIDE[name]
        fmt = lambda s: s.format(VAULT_ROOT=vault_root, USER_HOME=user_home)  # noqa: E731
        plist = {
            "Label": label,
            "ProgramArguments": [fmt(x) for x in ov["program"]],
            "WatchPaths": [fmt(w) for w in ov["watch"]],
            "StandardOutPath": f"{user_home}/Library/Logs/operator-harness/{name}.out.log",
            "StandardErrorPath": f"{user_home}/Library/Logs/operator-harness/{name}.err.log",
            "WorkingDirectory": vault_root,
        }
        return label, plist

    plist = {"Label": label, "ProgramArguments":
             build_program_args(name, exec_el, python, vault_root, user_home)}

    # log paths
    logdir = f"{user_home}/Library/Logs/operator-harness"
    plist["StandardOutPath"] = f"{logdir}/{name}.out.log"
    plist["StandardErrorPath"] = f"{logdir}/{name}.err.log"
    # working dir = vault
    plist["WorkingDirectory"] = vault_root

    is_daemon = False
    cal = []          # list of StartCalendarInterval dicts
    interval = None

    if triggers is not None:
        for trig in list(triggers):
            t = strip(trig.tag)
            if t in ("LogonTrigger", "BootTrigger"):
                is_daemon = True
            elif t == "TimeTrigger":
                rep = find(trig, "Repetition")
                if rep is not None and find(rep, "Interval") is not None:
                    interval = duration_to_seconds(find(rep, "Interval").text)
            elif t == "CalendarTrigger":
                sb = find(trig, "StartBoundary")
                hh, mm = iso_hh_mm(sb.text if sb is not None else "")
                # also honor a repetition on a calendar trigger -> treat as interval
                rep = find(trig, "Repetition")
                if rep is not None and find(rep, "Interval") is not None:
                    interval = duration_to_seconds(find(rep, "Interval").text)
                week = find(trig, "ScheduleByWeek")
                day = find(trig, "ScheduleByDay")
                if week is not None:
                    dows = find(week, "DaysOfWeek")
                    if dows is not None:
                        for d in list(dows):
                            wd = DOW.get(strip(d.tag))
                            if wd is not None:
                                cal.append({"Weekday": wd, "Hour": hh, "Minute": mm})
                    if not cal:
                        cal.append({"Hour": hh, "Minute": mm})
                elif day is not None:
                    cal.append({"Hour": hh, "Minute": mm})
                else:
                    cal.append({"Hour": hh, "Minute": mm})

    if is_daemon:
        plist["RunAtLoad"] = True
        plist["KeepAlive"] = True
    elif interval:
        plist["StartInterval"] = int(interval)
    elif cal:
        plist["StartCalendarInterval"] = cal[0] if len(cal) == 1 else cal
    else:
        # no recognizable trigger -> run at load once
        plist["RunAtLoad"] = True

    return label, plist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--python", default="/usr/bin/python3")
    ap.add_argument("--vault-root", required=True)
    ap.add_argument("--user-home", default=os.path.expanduser("~"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    vault_root = os.path.expanduser(a.vault_root)
    user_home = os.path.expanduser(a.user_home)
    out_dir = os.path.expanduser(a.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    xmls = sorted(f for f in os.listdir(a.tasks_dir) if f.endswith(".xml"))
    n = 0
    for f in xmls:
        try:
            res = convert(os.path.join(a.tasks_dir, f), a.python, vault_root, user_home)
        except Exception as e:
            print(f"  SKIP {f}: {e}", file=sys.stderr)
            continue
        if not res:
            continue
        label, plist = res
        out = os.path.join(out_dir, label + ".plist")
        if a.dry_run:
            print(f"  [dry] {label}: {plist.get('StartCalendarInterval') or plist.get('StartInterval') or ('daemon' if plist.get('KeepAlive') else 'once')}")
        else:
            with open(out, "wb") as fh:
                plistlib.dump(plist, fh)
            print(f"  wrote {os.path.basename(out)}")
        n += 1
    print(f"{'(dry) ' if a.dry_run else ''}{n} launchd plists from {len(xmls)} task XMLs")


if __name__ == "__main__":
    main()
