r"""
Cards weekly archive sweep — Sunday 22:00 CST.

Walks 02 Cards/{domain}/*.md (skipping _inbox, _archive, README).
For each card:
  - Parse `created:` frontmatter
  - If created > 90 days ago AND not wikilinked from anywhere in vault → move to 02 Cards/_archive/{domain}/

Wikilink detection: grep -r '\[\[Card-name' or '\[\[Card-filename-without-ext'.

Output: 04 Notes/auto-reports/YYYY-MM-DD-cards-archive.md
"""
from __future__ import annotations
import re
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

VAULT = Path(r"{{VAULT_ROOT}}")
CARDS_DIR = VAULT / "02 Cards"
REPORT_DIR = VAULT / "04 Notes" / "auto-reports"
AGE_DAYS = 90
SKIP_DIRS = {"_inbox", "_archive", "meta"}  # meta cards never auto-archive
SKIP_FILES = {"(C) README.md", "_index.base"}

FM_DATE_RE = re.compile(r"^\s*created\s*:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def parse_created(text: str) -> date | None:
    m = FM_DATE_RE.search(text[:1500])  # frontmatter only
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


def is_referenced(card_path: Path) -> tuple[bool, list[str]]:
    """Check if card is wikilinked from anywhere in vault (outside its own file)."""
    slug = card_path.stem  # e.g. "C260424-honor-channel-fills..."
    patterns = [
        f"[[{slug}",  # full slug
        f"[[02 Cards/{card_path.parent.name}/{slug}",  # qualified
    ]
    refs = []
    for pat in patterns:
        try:
            result = subprocess.run(
                ["grep", "-rl", "--include=*.md", "-F", pat, str(VAULT)],
                capture_output=True, text=True, timeout=30,
            )
            for line in result.stdout.splitlines():
                p = Path(line.strip())
                if p.resolve() != card_path.resolve() and p.exists():
                    refs.append(str(p.relative_to(VAULT)))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    return (len(refs) > 0, sorted(set(refs)))


def main():
    today = date.today()
    cutoff = today - timedelta(days=AGE_DAYS)
    candidates: list[dict] = []
    moved: list[dict] = []
    skipped_unreferenceable: list[dict] = []

    for card in CARDS_DIR.rglob("*.md"):
        rel = card.relative_to(CARDS_DIR)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if card.name in SKIP_FILES:
            continue
        try:
            text = card.read_text(encoding="utf-8")
        except Exception:
            continue
        created = parse_created(text)
        if not created or created > cutoff:
            continue
        referenced, refs = is_referenced(card)
        item = {"path": str(rel), "created": str(created), "refs": refs}
        if referenced:
            skipped_unreferenceable.append(item)
            continue
        # Move to _archive
        archive_dir = CARDS_DIR / "_archive" / rel.parent
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest = archive_dir / card.name
        if dest.exists():
            dest = archive_dir / f"{card.stem}-{today.isoformat()}{card.suffix}"
        shutil.move(str(card), str(dest))
        item["archived_to"] = str(dest.relative_to(VAULT))
        moved.append(item)
        candidates.append(item)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{today.isoformat()}-cards-archive.md"
    md = [
        "---",
        "type: auto-report",
        "report: cards-archive",
        f"date: {today.isoformat()}",
        f"age-threshold-days: {AGE_DAYS}",
        f"archived: {len(moved)}",
        f"kept-due-to-references: {len(skipped_unreferenceable)}",
        "biz-eval: skip",
        "---",
        "",
        f"# Cards Archive Sweep · {today.isoformat()}",
        "",
        f"Criteria: `created` ≥ {AGE_DAYS} days ago **AND** no other vault file wikilinks to it.",
        f"`02 Cards/_archive/<domain>/`-bound. Reversible — move back if revisiting.",
        "",
        f"**Moved: {len(moved)}** · **Kept (referenced): {len(skipped_unreferenceable)}**",
        "",
    ]
    if moved:
        md += ["## Moved to _archive", ""]
        for it in moved:
            md.append(f"- `{it['path']}` (created {it['created']}) → `{it['archived_to']}`")
        md.append("")
    if skipped_unreferenceable:
        md += ["## Kept (referenced from)", ""]
        for it in skipped_unreferenceable:
            ref_list = ", ".join(f"`{r}`" for r in it["refs"][:3])
            more = f" + {len(it['refs']) - 3} more" if len(it["refs"]) > 3 else ""
            md.append(f"- `{it['path']}` (created {it['created']}) ← {ref_list}{more}")
        md.append("")
    if not candidates and not skipped_unreferenceable:
        md.append("✅ No cards older than threshold. Card pool is fresh.")
        md.append("")
    report_path.write_text("\n".join(md), encoding="utf-8")
    print(f"cards-archive: moved {len(moved)}, kept {len(skipped_unreferenceable)} (referenced). Report: {report_path}")


if __name__ == "__main__":
    sys.exit(main())
