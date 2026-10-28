#!/usr/bin/env python3
"""Find and fix stale jp-tosca/dv-modern-fc references in the IQSS issues.

The gap issues were drafted in jp-tosca/dv-modern-fc (the "mockup" issues),
reviewed, and the valid ones re-opened in IQSS/dataverse-frontend. Their
bodies were copied across, so they still cite each other as
`jp-tosca/dv-modern-fc#5`, as full URLs, or as bare `#7` shorthand that now
silently resolves to the wrong IQSS issue. This script rewrites only those
reference tokens, and only to the IQSS issue that replaced the mockup.

Commands (run in this order; each reads what the previous one wrote):
  fetch                         snapshot both repos' issues (+ comments) via gh
  map [--set JP IQSS] [--confirm JP] [--none JP]
                                build/review the jp -> IQSS correspondence
  scan                          find references, write the plan (no edits)
  decide ID accept|reject --reason TEXT
                                resolve a finding the scan marked 'review'
  apply [--yes]                 dry-run by default; --yes edits GitHub
  report                        markdown report of what changed and what didn't

State lives in automation/iqss-refs/ (override with --data-dir):
  snapshot.json  jp-to-iqss-map.tsv  plan.json  changes.tsv  backup/  report-*.md
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

MOCKUP_REPO = "jp-tosca/dv-modern-fc"
TARGET_REPO = "IQSS/dataverse-frontend"
MAP_FIELDS = ["jp", "iqss", "status", "score", "runner_up", "jp_title", "iqss_title"]
# statuses whose iqss value scan may use; 'review' and 'none' are reported as unmapped
USABLE = {"auto", "confirmed", "manual"}
CHANGE_FIELDS = ["date", "plan_id", "finding", "repo", "issue", "unit", "before",
                 "after", "jp", "iqss", "url"]
# a bare #N continues a list started by a jp-qualified ref only across this much text
CHAIN_GAP = 160


def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        return subprocess.run(
            ["git", "-C", here, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit(f"{here} is not inside a git checkout")


def gh_json_lines(*args):
    """Run `gh api ... --jq '.[]'` and parse one JSON object per line."""
    out = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"gh api {' '.join(args)} failed:\n{out.stderr}")
    return [json.loads(ln) for ln in out.stdout.splitlines() if ln.strip()]


def gh(*args, stdin=None):
    out = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"gh {' '.join(args)} failed:\n{out.stderr}")
    return out.stdout


def sha(text):
    return hashlib.sha256((text or "").encode()).hexdigest()[:16]


def load_json(path, what):
    if not os.path.exists(path):
        sys.exit(f"{os.path.basename(path)} not found - run `{what}` first")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)


# --- fetch -------------------------------------------------------------------

def list_issues(repo, creator=None):
    args = ["-X", "GET", f"repos/{repo}/issues", "-f", "state=all", "-f",
            "per_page=100", "--paginate", "--jq", ".[]"]
    if creator:
        args += ["-f", f"creator={creator}"]
    return [i for i in gh_json_lines(*args) if "pull_request" not in i]


def cmd_fetch(a, d):
    login = gh("api", "user", "--jq", ".login").strip()
    jp = [{"number": i["number"], "title": i["title"], "state": i["state"],
           "body": i["body"] or ""} for i in list_issues(MOCKUP_REPO)]
    iqss = []
    for i in list_issues(a.repo, creator=login):
        comments = gh_json_lines(f"repos/{a.repo}/issues/{i['number']}/comments",
                                 "--paginate", "--jq", ".[]") if i["comments"] else []
        iqss.append({
            "number": i["number"], "title": i["title"], "state": i["state"],
            "body": i["body"] or "", "url": i["html_url"],
            "comments": [{"id": c["id"], "author": c["user"]["login"],
                          "body": c["body"] or "", "url": c["html_url"]} for c in comments],
        })
    save_json(d["snapshot"], {
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "login": login, "repo": a.repo, "jp": jp, "iqss": iqss})
    print(f"snapshot: {len(jp)} {MOCKUP_REPO} issues, {len(iqss)} {a.repo} issues "
          f"opened by {login} ({sum(len(i['comments']) for i in iqss)} comments)")


# --- map ---------------------------------------------------------------------

def shingles(text):
    w = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {" ".join(w[i:i + 5]) for i in range(len(w) - 4)}


def read_map(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8", newline="") as fh:
        return {int(r["jp"]): r for r in csv.DictReader(fh, delimiter="\t")}


def write_map(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MAP_FIELDS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for k in sorted(rows):
            w.writerow(rows[k])


def cmd_map(a, d):
    snap = load_json(d["snapshot"], "fetch")
    rows = read_map(d["map"])
    iq_titles = {i["number"]: i["title"] for i in snap["iqss"]}
    if a.set or a.confirm or a.none:
        if a.set:
            jp, iq = a.set
            rows[jp].update(iqss=str(iq), status="manual", iqss_title=iq_titles.get(iq, ""))
        if a.confirm:
            if not rows[a.confirm]["iqss"]:
                sys.exit(f"jp #{a.confirm} has no suggested IQSS issue to confirm; use --set")
            rows[a.confirm]["status"] = "confirmed"
        if a.none:
            rows[a.none].update(iqss="", status="none", iqss_title="")
        write_map(d["map"], rows)
    else:
        cands = [(i["number"], shingles(i["title"] + " " + i["body"])) for i in snap["iqss"]]
        for j in snap["jp"]:
            if rows.get(j["number"], {}).get("status") in ("confirmed", "manual", "none"):
                continue  # a human decision; never overwrite it
            s = shingles(j["title"] + " " + j["body"])
            scored = sorted(((len(s & c) / max(1, len(s | c)), n) for n, c in cands),
                            reverse=True) or [(0, None)]
            best, num = scored[0]
            runner = scored[1][0] if len(scored) > 1 else 0
            # copied bodies score ~0.9+; unrelated ones stay under ~0.25
            status = ("auto" if best >= 0.6 and best - runner >= 0.3
                      else "review" if best >= 0.3 else "none")
            rows[j["number"]] = {
                "jp": j["number"], "iqss": num if status != "none" else "",
                "status": status, "score": f"{best:.2f}", "runner_up": f"{runner:.2f}",
                "jp_title": j["title"],
                "iqss_title": iq_titles.get(num, "") if status != "none" else ""}
        write_map(d["map"], rows)
    print("| jp | IQSS | status | score | runner-up | jp title | IQSS title |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for k in sorted(rows):
        r = rows[k]
        iq = f"#{r['iqss']}" if r["iqss"] else "—"
        print(f"| #{k} | {iq} | {r['status']} | {r['score']} | {r['runner_up']} "
              f"| {r['jp_title'][:60]} | {r['iqss_title'][:60]} |")


# --- scan --------------------------------------------------------------------

TOKEN = re.compile(
    r"(?P<url>https?://github\.com/jp-tosca/dv-modern-fc/issues/(?P<url_n>\d+)(?P<frag>#[\w-]+)?)"
    r"|(?P<qual>(?<![\w/.-])jp-tosca/dv-modern-fc#(?P<qual_n>\d+)\b)"
    r"|(?P<other>https?://github\.com/[\w.-]+/[\w.-]+/(?:issues|pull)/\d+"
    r"|(?<![\w/.-])[\w.-]+/[\w.-]+#\d+\b)"
    r"|(?P<bare>(?<![\w/&#.-])#(?P<bare_n>\d+)\b)",
    re.I)
OTHER_JP_LINK = re.compile(
    r"https?://(?:github\.com|raw\.githubusercontent\.com)/jp-tosca/dv-modern-fc"
    r"(?!/issues/\d)[^\s)\]>\"']*", re.I)


def code_spans(text):
    spans = [m.span() for m in re.finditer(r"```.*?(?:```|\Z)", text, re.S)]
    spans += [m.span() for m in re.finditer(r"`[^`\n]+`", text)]
    return spans


def context(text, s, e, width=70):
    return text[max(0, s - width):e + width].replace("\r", "").replace("\n", " ⏎ ")


def find_refs(text, jp_numbers):
    """Yield (start, end, token, kind, jp_number, note) for each stale candidate."""
    anchor = None  # end offset of the last jp reference a bare #N may chain onto
    for m in TOKEN.finditer(text):
        s, e = m.span()
        if m.group("url"):
            note = "URL carries a #fragment (jp comment anchor) that has no IQSS equivalent" \
                if m.group("frag") else ""
            anchor = e
            yield s, e, m.group(0), "url", int(m.group("url_n")), note
        elif m.group("qual"):
            anchor = e
            yield s, e, m.group(0), "qualified", int(m.group("qual_n")), ""
        elif m.group("other"):
            anchor = None
        else:
            n = int(m.group("bare_n"))
            if n not in jp_numbers:
                anchor = None
                continue
            gap = text[anchor:s] if anchor is not None else None
            if gap is not None and len(gap) <= CHAIN_GAP and "\n" not in gap:
                anchor = e
                yield s, e, m.group(0), "bare-chain", n, ""
            else:
                anchor = None
                yield s, e, m.group(0), "bare-review", n, \
                    "bare #N not attached to a jp-qualified ref; may be a real IQSS ref"


def cmd_scan(a, d):
    snap = load_json(d["snapshot"], "fetch")
    rows = read_map(d["map"])
    if not rows:
        sys.exit("jp-to-iqss-map.tsv is empty - run `map` first")
    pending = [k for k, r in rows.items() if r["status"] == "review"]
    if pending:
        print(f"warning: map rows still in 'review' (treated as unmapped): {pending}")
    jp_title = {j["number"]: j["title"] for j in snap["jp"]}
    mapping = {k: int(r["iqss"]) for k, r in rows.items()
               if r["status"] in USABLE and r["iqss"]}
    repo, login = snap["repo"], snap["login"]
    local_titles = {}

    def local_title(n):
        if n not in local_titles:
            out = subprocess.run(["gh", "api", f"repos/{repo}/issues/{n}", "--jq", ".title"],
                                 capture_output=True, text=True)
            local_titles[n] = out.stdout.strip() if out.returncode == 0 else "(not found)"
        return local_titles[n]

    findings, units, other_links = [], {}, []
    for iss in snap["iqss"]:
        unit_list = [("body", iss["body"], True, iss["url"])]
        unit_list += [(f"comment:{c['id']}", c["body"], c["author"] == login, c["url"])
                      for c in iss["comments"]]
        for unit, text, editable, url in unit_list:
            units[f"{iss['number']}/{unit}"] = {"sha": sha(text), "url": url}
            spans = code_spans(text)
            for s, e, tok, kind, jp, note in find_refs(text, set(jp_title)):
                iq = mapping.get(jp)
                in_code = any(cs <= s < ce for cs, ce in spans)
                if kind in ("qualified", "bare-chain", "bare-review"):
                    repl = f"#{iq}" if repo == TARGET_REPO else f"{TARGET_REPO}#{iq}"
                else:
                    repl = f"https://github.com/{TARGET_REPO}/issues/{iq}"
                if iq is None:
                    status, repl = "unmapped", None
                    note = note or "no IQSS counterpart in the map; left unchanged"
                elif not editable:
                    status, note = "readonly", "comment by someone else; not edited"
                elif iq == iss["number"]:
                    status, note = "review", "mapped issue is this issue itself"
                elif in_code:
                    status, note = "review", "inside a code span; may be literal text"
                elif kind == "bare-review" or note:
                    status = "review"
                else:
                    status = "auto"
                f = {"id": f"F{len(findings) + 1}", "issue": iss["number"],
                     "issue_title": iss["title"], "unit": unit, "url": url,
                     "start": s, "end": e, "before": tok, "after": repl,
                     "kind": kind, "jp": jp, "jp_title": jp_title.get(jp, ""),
                     "iqss": iq, "status": status, "note": note,
                     "decision": "accept" if status == "auto" else None,
                     "reason": "", "context": context(text, s, e)}
                if kind == "bare-review":
                    f["local_title"] = local_title(jp)  # what #N means in the IQSS repo today
                findings.append(f)
            other_links += [{"issue": iss["number"], "unit": unit, "link": m.group(0)}
                            for m in OTHER_JP_LINK.finditer(text)]
    plan = {"plan_id": datetime.datetime.now().strftime("%Y%m%dT%H%M%S"),
            "snapshot_at": snap["fetched_at"], "repo": repo, "units": units,
            "findings": findings, "other_links": other_links}
    save_json(d["plan"], plan)
    print_plan(plan)


def print_plan(plan):
    counts = {}
    for f in plan["findings"]:
        counts[f["status"]] = counts.get(f["status"], 0) + 1
    print(f"plan {plan['plan_id']}: {len(plan['findings'])} references "
          + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    for f in plan["findings"]:
        dec = f["decision"] or "UNDECIDED"
        arrow = f"{f['before']} -> {f['after']}" if f["after"] else f"{f['before']} (no change)"
        print(f"\n{f['id']} [{f['status']}/{dec}] #{f['issue']} {f['unit']} {f['kind']}: {arrow}")
        print(f"   jp #{f['jp']}: {f['jp_title'][:80]}")
        if f.get("local_title"):
            print(f"   {plan['repo']}#{f['jp']} today: {f['local_title'][:80]}")
        if f["note"]:
            print(f"   note: {f['note']}")
        print(f"   …{f['context']}…")
    if plan["other_links"]:
        print(f"\n{len(plan['other_links'])} other jp-tosca links (not issue refs, never edited):")
        for o in plan["other_links"]:
            print(f"   #{o['issue']} {o['unit']}: {o['link']}")


def cmd_decide(a, d):
    plan = load_json(d["plan"], "scan")
    f = next((f for f in plan["findings"] if f["id"] == a.id), None)
    if not f:
        sys.exit(f"no finding {a.id}")
    if a.verdict == "accept" and f["status"] not in ("review", "auto"):
        sys.exit(f"{a.id} is '{f['status']}' and cannot be accepted")
    f["decision"], f["reason"] = a.verdict, a.reason
    save_json(d["plan"], plan)
    print(f"{a.id}: {a.verdict} ({a.reason})")


# --- apply -------------------------------------------------------------------

def fetch_unit(repo, issue, unit):
    path = (f"repos/{repo}/issues/{issue}" if unit == "body"
            else f"repos/{repo}/issues/comments/{unit.split(':', 1)[1]}")
    return json.loads(gh("api", path))["body"] or ""


def patch_unit(repo, issue, unit, body):
    path = (f"repos/{repo}/issues/{issue}" if unit == "body"
            else f"repos/{repo}/issues/comments/{unit.split(':', 1)[1]}")
    gh("api", "-X", "PATCH", path, "--input", "-", stdin=json.dumps({"body": body}))


def cmd_apply(a, d):
    plan = load_json(d["plan"], "scan")
    undecided = [f["id"] for f in plan["findings"] if f["status"] == "review" and not f["decision"]]
    if undecided:
        sys.exit(f"undecided review findings: {', '.join(undecided)} - use `decide` first")
    todo = {}
    for f in plan["findings"]:
        if f["decision"] == "accept" and f["after"]:
            todo.setdefault((f["issue"], f["unit"]), []).append(f)
    if not todo:
        print("nothing to apply")
        return
    repo = plan["repo"]
    if not a.yes:
        for (issue, unit), fs in sorted(todo.items()):
            print(f"\n#{issue} {unit}: {len(fs)} replacement(s)")
            for f in fs:
                print(f"   {f['id']} {f['before']} -> {f['after']}")
        print("\ndry run - nothing was edited. Re-run with --yes to apply.")
        return
    os.makedirs(d["backup"], exist_ok=True)
    new_log = not os.path.exists(d["changes"])
    log = open(d["changes"], "a", encoding="utf-8", newline="")
    w = csv.DictWriter(log, fieldnames=CHANGE_FIELDS, delimiter="\t", lineterminator="\n")
    if new_log:
        w.writeheader()
    for (issue, unit), fs in sorted(todo.items()):
        key = f"{issue}/{unit}"
        print(f"\n#{issue} {unit}: {len(fs)} replacement(s)")
        current = fetch_unit(repo, issue, unit)
        if sha(current) != plan["units"][key]["sha"]:
            print("   SKIPPED: text changed on GitHub since the scan; re-run fetch + scan")
            w.writerow({"date": datetime.date.today().isoformat(), "plan_id": plan["plan_id"],
                        "finding": ",".join(f["id"] for f in fs), "repo": repo, "issue": issue,
                        "unit": unit, "before": "SKIPPED: changed since scan", "after": "",
                        "jp": "", "iqss": "", "url": plan["units"][key]["url"]})
            continue
        new = current
        for f in sorted(fs, key=lambda f: f["start"], reverse=True):
            assert new[f["start"]:f["end"]] == f["before"], f["id"]
            new = new[:f["start"]] + f["after"] + new[f["end"]:]
        stamp = plan["plan_id"]
        with open(os.path.join(d["backup"], f"{issue}-{unit.replace(':', '-')}-{stamp}.md"),
                  "w", encoding="utf-8", newline="") as fh:
            fh.write(current)
        patch_unit(repo, issue, unit, new)
        ok = fetch_unit(repo, issue, unit) == new
        print("   applied and verified" if ok else "   WARNING: re-read differs from what was sent")
        for f in fs:
            w.writerow({"date": datetime.date.today().isoformat(), "plan_id": stamp,
                        "finding": f["id"], "repo": repo, "issue": issue, "unit": unit,
                        "before": f["before"], "after": f["after"] + ("" if ok else " (UNVERIFIED)"),
                        "jp": f["jp"], "iqss": f["iqss"], "url": f["url"]})
    log.close()


# --- report ------------------------------------------------------------------

def cmd_report(a, d):
    plan = load_json(d["plan"], "scan")
    applied = []
    if os.path.exists(d["changes"]):
        with open(d["changes"], encoding="utf-8", newline="") as fh:
            applied = [r for r in csv.DictReader(fh, delimiter="\t")
                       if r["plan_id"] == plan["plan_id"]]
    done = {r["finding"] for r in applied if not r["before"].startswith("SKIPPED")}
    skipped = [r for r in applied if r["before"].startswith("SKIPPED")]
    def by(status):
        return [f for f in plan["findings"] if f["status"] == status]

    rejected = [f for f in plan["findings"] if f["decision"] == "reject"]
    accepted_not_done = [f for f in plan["findings"] if f["decision"] == "accept"
                         and f["after"] and f["id"] not in done]
    repo = plan["repo"]
    L = [f"# Stale mockup-reference check — {repo}", "",
         f"Plan `{plan['plan_id']}` · snapshot {plan['snapshot_at']} · "
         f"{len(plan['units'])} bodies/comments scanned", "",
         "| | Count |", "| --- | --- |",
         f"| References to {MOCKUP_REPO} issues found | {len(plan['findings'])} |",
         f"| Updated | {len(done)} |",
         f"| Not updated: no IQSS counterpart | {len(by('unmapped'))} |",
         f"| Not updated: someone else's comment | {len(by('readonly'))} |",
         f"| Not updated: rejected on review | {len(rejected)} |",
         f"| Not updated: changed on GitHub since scan | {len(skipped)} |",
         f"| Accepted but not applied (dry run only) | {len(accepted_not_done)} |", ""]
    L += ["## Updated", ""]
    if done:
        L += ["| Issue | Where | Before | After | Mockup issue |", "| --- | --- | --- | --- | --- |"]
        for f in plan["findings"]:
            if f["id"] in done:
                L.append(f"| [{repo}#{f['issue']}]({f['url']}) | {f['unit']} | `{f['before']}` "
                         f"| `{f['after']}` | jp #{f['jp']}: {f['jp_title'][:70]} |")
    else:
        L.append("Nothing was edited.")

    def section(title, fs, why):
        if not fs:
            return []
        out = ["", f"## {title}", "", "| Issue | Where | Reference | Mockup issue | Why |",
               "| --- | --- | --- | --- | --- |"]
        for f in fs:
            out.append(f"| [{repo}#{f['issue']}]({f['url']}) | {f['unit']} | `{f['before']}` "
                       f"| jp #{f['jp']}: {f['jp_title'][:70]} | {why(f)} |")
        return out
    L += section("Still pointing at the mockup repo — no IQSS counterpart", by("unmapped"),
                 lambda f: "not migrated; add one with `map --set` if an equivalent exists")
    L += section("In other people's comments (not edited)", by("readonly"),
                 lambda f: f"would map to #{f['iqss']}" if f["iqss"] else "unmapped")
    L += section("Rejected on review", rejected, lambda f: f["reason"] or f["note"])
    L += section("Accepted but not applied", accepted_not_done,
                 lambda f: "skipped (changed since scan)" if any(
                     f["id"] in r["finding"].split(",") for r in skipped) else "apply not run with --yes")
    if plan["other_links"]:
        L += ["", "## Other jp-tosca links (not issue references, left as is)", ""]
        L += [f"- {repo}#{o['issue']} {o['unit']}: {o['link']}" for o in plan["other_links"]]
    text = "\n".join(L) + "\n"
    path = os.path.join(d["dir"], f"report-{plan['plan_id']}.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    print(f"(saved to {os.path.relpath(path, repo_root())})")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", help="state directory (default automation/iqss-refs)")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--repo", default=TARGET_REPO, help="repo whose issues (opened by you) are checked")
    m = sub.add_parser("map")
    m.add_argument("--set", nargs=2, type=int, metavar=("JP", "IQSS"))
    m.add_argument("--confirm", type=int, metavar="JP")
    m.add_argument("--none", type=int, metavar="JP")
    sub.add_parser("scan")
    de = sub.add_parser("decide")
    de.add_argument("id")
    de.add_argument("verdict", choices=["accept", "reject"])
    de.add_argument("--reason", required=True)
    ap = sub.add_parser("apply")
    ap.add_argument("--yes", action="store_true", help="actually edit GitHub")
    sub.add_parser("report")
    a = p.parse_args()

    base = a.data_dir or os.path.join(repo_root(), "automation", "iqss-refs")
    os.makedirs(base, exist_ok=True)
    d = {"dir": base, "snapshot": os.path.join(base, "snapshot.json"),
         "map": os.path.join(base, "jp-to-iqss-map.tsv"), "plan": os.path.join(base, "plan.json"),
         "changes": os.path.join(base, "changes.tsv"), "backup": os.path.join(base, "backup")}
    {"fetch": cmd_fetch, "map": cmd_map, "scan": cmd_scan, "decide": cmd_decide,
     "apply": cmd_apply, "report": cmd_report}[a.cmd](a, d)


if __name__ == "__main__":
    main()
