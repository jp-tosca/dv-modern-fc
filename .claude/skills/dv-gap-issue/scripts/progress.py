#!/usr/bin/env python3
"""Track which rows of `DV - Missing items.md` have been researched.

The missing-items list has ~230 rows and is processed one item at a time,
often across several sessions, so the queue position has to live on disk
rather than in the conversation. This script is the single source of truth
for "what is next" and "what happened to the items already done".

Commands:
  next [--count N]                 show the next unprocessed item(s), full detail
  show --idx N                     show one item by index
  find <text>                      search the list (page/functionality/description)
  record --idx N --result ... --action ...   append a decision to the progress file
  status                           counts by action, plus the next index
  table [--last N] [--all]         render the progress table as markdown

Progress lives in automation/dv-gap-progress.tsv (TSV to match the repo's
convention of TSV sources backing markdown tables).
"""
import argparse
import csv
import os
import subprocess
import sys

LIST_NAME = "DV - Missing items.md"
PROGRESS_REL = os.path.join("automation", "dv-gap-progress.tsv")
FIELDS = [
    "idx", "page", "functionality", "verification_result",
    "related_issues", "action", "created_issue", "notes", "date",
]
ACTIONS = [
    "issue-created", "duplicate", "already-implemented",
    "upstream-covered", "not-reproducible", "skipped",
]


def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        root = subprocess.run(
            ["git", "-C", here, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        root = ""
    if root and os.path.exists(os.path.join(root, LIST_NAME)):
        return root
    # fall back to walking up from the skill directory
    d = here
    while d != "/":
        if os.path.exists(os.path.join(d, LIST_NAME)):
            return d
        d = os.path.dirname(d)
    sys.exit(f"could not locate '{LIST_NAME}' in any parent directory of {here}")


ROOT = repo_root()
LIST_PATH = os.path.join(ROOT, LIST_NAME)
PROGRESS_PATH = os.path.join(ROOT, PROGRESS_REL)


def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def load_items():
    """Return the missing-items rows as dicts, indexed from 1 in file order."""
    with open(LIST_PATH, encoding="utf-8") as fh:
        lines = [ln for ln in fh if ln.strip().startswith("|")]
    header = split_row(lines[0])
    items = []
    for n, line in enumerate(lines[2:], start=1):  # skip header + separator
        cells = split_row(line)
        row = dict(zip(header, cells + [""] * (len(header) - len(cells))))
        row["idx"] = n
        items.append(row)
    return header, items


def load_progress():
    if not os.path.exists(PROGRESS_PATH):
        return []
    with open(PROGRESS_PATH, newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t") if r.get("idx")]


def done_indexes(progress):
    return {int(r["idx"]) for r in progress if str(r["idx"]).isdigit()}


def fmt_item(item, header):
    out = [f"### item {item['idx']}: {item.get('Page','')} - {item.get('Functionality','')}"]
    for col in header:
        if col in ("Page", "Functionality"):
            continue
        val = item.get(col, "")
        if val:
            out.append(f"- **{col}**: {val}")
    return "\n".join(out)


def cmd_next(args):
    header, items = load_items()
    done = done_indexes(load_progress())
    pending = [i for i in items if i["idx"] not in done]
    if not pending:
        print(f"All {len(items)} items processed.")
        return
    print(f"{len(done)} of {len(items)} processed; {len(pending)} remaining.\n")
    for item in pending[: args.count]:
        print(fmt_item(item, header))
        print()


def cmd_show(args):
    header, items = load_items()
    for item in items:
        if item["idx"] == args.idx:
            print(fmt_item(item, header))
            return
    sys.exit(f"no item with idx {args.idx} (list has {len(items)} rows)")


def cmd_find(args):
    header, items = load_items()
    done = done_indexes(load_progress())
    needle = " ".join(args.text).lower()
    hits = [i for i in items
            if needle in " ".join(i.get(c, "") for c in header).lower()]
    if not hits:
        print("no matches")
        return
    for item in hits:
        mark = "done" if item["idx"] in done else "pending"
        print(f"{item['idx']:>4}  [{mark:>7}]  {item.get('Page','')} - {item.get('Functionality','')}")


def cmd_record(args):
    header, items = load_items()
    match = [i for i in items if i["idx"] == args.idx]
    if not match:
        sys.exit(f"no item with idx {args.idx}")
    item = match[0]
    progress = load_progress()
    if args.idx in done_indexes(progress) and not args.force:
        sys.exit(f"item {args.idx} is already recorded; pass --force to overwrite")
    progress = [r for r in progress if int(r["idx"]) != args.idx]
    progress.append({
        "idx": str(args.idx),
        "page": item.get("Page", ""),
        "functionality": item.get("Functionality", ""),
        "verification_result": args.result,
        "related_issues": args.related or "None found",
        "action": args.action,
        "created_issue": args.issue or "",
        "notes": args.notes or "",
        "date": args.date or __import__("datetime").date.today().isoformat(),
    })
    progress.sort(key=lambda r: int(r["idx"]))
    os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
    with open(PROGRESS_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t")
        w.writeheader()
        w.writerows(progress)
    print(f"recorded item {args.idx} ({args.action}) -> {PROGRESS_REL}")


def cmd_status(args):
    _, items = load_items()
    progress = load_progress()
    counts = {}
    for r in progress:
        counts[r["action"]] = counts.get(r["action"], 0) + 1
    print(f"list: {len(items)} items | processed: {len(progress)} | remaining: {len(items) - len(progress)}")
    for action in ACTIONS:
        if counts.get(action):
            print(f"  {action}: {counts[action]}")
    for action, n in sorted(counts.items()):
        if action not in ACTIONS:
            print(f"  {action} (non-standard): {n}")
    done = done_indexes(progress)
    nxt = next((i["idx"] for i in items if i["idx"] not in done), None)
    print(f"next unprocessed item: {nxt if nxt else 'none - list complete'}")


def cmd_table(args):
    progress = load_progress()
    if not progress:
        print("no progress recorded yet")
        return
    rows = progress if args.all else progress[-args.last:]
    print("| Missing-list item | Verification result | Related issues | Action | Created issue |")
    print("| --- | --- | --- | --- | --- |")
    for r in rows:
        item = f"{r['idx']}. {r['page']} - {r['functionality']}"
        print(f"| {item} | {r['verification_result']} | {r['related_issues']} | "
              f"{r['action']} | {r['created_issue'] or '-'} |")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("next", help="show the next unprocessed item(s)")
    s.add_argument("--count", type=int, default=1)
    s.set_defaults(func=cmd_next)

    s = sub.add_parser("show", help="show one item by index")
    s.add_argument("--idx", type=int, required=True)
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("find", help="search the missing-items list")
    s.add_argument("text", nargs="+")
    s.set_defaults(func=cmd_find)

    s = sub.add_parser("record", help="append a decision to the progress file")
    s.add_argument("--idx", type=int, required=True)
    s.add_argument("--result", required=True, help="what verification showed")
    s.add_argument("--action", required=True, choices=ACTIONS)
    s.add_argument("--related", help="related issue refs, or 'None found'")
    s.add_argument("--issue", help="URL of the issue created, if any")
    s.add_argument("--notes")
    s.add_argument("--date")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_record)

    s = sub.add_parser("status", help="counts by action and the next index")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("table", help="render the progress table as markdown")
    s.add_argument("--last", type=int, default=10)
    s.add_argument("--all", action="store_true")
    s.set_defaults(func=cmd_table)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
