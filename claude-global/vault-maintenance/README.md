# Vault Maintenance Scripts

3 weekly Python scripts + 1 daily Anthropic remote routine, keeping the vault hygienic so {{USER_NAME}} doesn't have to.

## Scripts

| Script | Schedule | What it does | Output |
|---|---|---|---|
| `inbox-decay.py` | Sun 21:00 CST | Tags `#stale` on `- [ ]` items in `06 Tasks/Inbox.md` + `Tasks.md` whose `📅` date is > 14 days old | `04 Notes/auto-reports/YYYY-MM-DD-inbox-decay.md` |
| `cards-archive.py` | Sun 22:00 CST | Moves cards (`created` > 90 days ago AND no incoming wikilinks) from `02 Cards/<domain>/` to `02 Cards/_archive/<domain>/` | `04 Notes/auto-reports/YYYY-MM-DD-cards-archive.md` |
| `weekly-metabolism.py` | Fri 18:00 CST | Tasks Kanban health table (open/overdue/done-7d) per surface, cards spawned by domain, daily-note coverage | `04 Notes/auto-reports/YYYY-MM-DD-metabolism.md` |

## Remote routines (claude.ai)

| Routine | Schedule | What |
|---|---|---|
| `Anthropic Doc Skills · Weekly Update Check` | Mon 09:00 CST | Emails {{USER_NAME}} when `anthropics/skills` repo has new commits to docx/pptx/xlsx/pdf |
| `Daily EOD Reminder · 22:00 weekday` | Mon-Fri 22:00 CST | Emails {{USER_NAME}} a reminder to run `/daily-note --close` for that day |

## Installation

```powershell
# Run once as your normal user (no admin needed)
powershell -ExecutionPolicy Bypass -File {{USER_HOME}}\.claude\vault-maintenance\register-win-tasks.ps1
```

Idempotent — re-run anytime to refresh task registration.

## Manual run (testing)

```bash
python {{USER_HOME}}\.claude\vault-maintenance\inbox-decay.py
python {{USER_HOME}}\.claude\vault-maintenance\cards-archive.py
python {{USER_HOME}}\.claude\vault-maintenance\weekly-metabolism.py
```

Or via Task Scheduler:
```powershell
Start-ScheduledTask -TaskName "RG-vault-weekly-metabolism"
```

## Where reports land

All reports go to `04 Notes/auto-reports/YYYY-MM-DD-<report>.md` with frontmatter `type: auto-report` + `biz-eval: skip`. They're vault-resident so they integrate with Bases / Dataview if {{USER_NAME}} wants to query them.

## Tuning knobs

- `inbox-decay.py` — `THRESHOLD_DAYS = 14` (top of file)
- `cards-archive.py` — `AGE_DAYS = 90`, `SKIP_DIRS` (meta cards never auto-archive)
- `weekly-metabolism.py` — window hardcoded to 7 days

## Removal

```powershell
schtasks /Delete /TN "RG-vault-inbox-decay" /F
schtasks /Delete /TN "RG-vault-cards-archive" /F
schtasks /Delete /TN "RG-vault-weekly-metabolism" /F
```

For the two remote routines, manage at https://claude.ai/code/routines.
