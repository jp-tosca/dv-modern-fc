#!/usr/bin/env python3
"""Label the issues in a GitHub Projects view with the user role they serve.

Four audiences are recognised, each mapped onto the `User Role: *` labels that
already exist in the IQSS repositories:

  curator    Curator               -> User Role: Curator
  depositor  Data Depositor        -> User Role: Depositor
  seeker     Data Seeker           -> User Role: Guest
  sysadmin   Installation Manager  -> User Role: Sysadmin   (server, config, deploy)
  superuser  Installation Manager  -> User Role: Superuser  (in-app admin tools)

The classification itself is a judgment made by whoever runs the skill and is
recorded in decisions.tsv; this script only fetches, validates, applies and
reports.

Commands (run in this order; each reads what the previous one wrote):
  fetch [--owner IQSS --project 34 --view 52]
                       snapshot every project item, apply the view's filter
  list [--offset N --limit N] [--body CHARS]
                       print the in-scope issues for classification
  check                validate decisions.tsv against the scope
  apply [--yes]        dry run by default; --yes adds labels on GitHub
  report               markdown report of what was labelled and what wasn't

State lives in automation/user-roles/ (override with --data-dir):
  items.json  scope.json  decisions.tsv  applied.tsv  report-*.md
"""
import argparse
import csv
import datetime
import fnmatch
import json
import os
import re
import subprocess
import sys

ROLE_LABELS = {
    "curator": "User Role: Curator",
    "depositor": "User Role: Depositor",
    "seeker": "User Role: Guest",
    "sysadmin": "User Role: Sysadmin",
    "superuser": "User Role: Superuser",
}
ROLE_NAMES = {
    "curator": "Curator",
    "depositor": "Data Depositor",
    "seeker": "Data Seeker",
    "sysadmin": "Installation Manager (Sysadmin)",
    "superuser": "Installation Manager (Superuser)",
}
# any existing label with this prefix means a human already classified the issue
ROLE_PREFIX = "User Role:"
DECISION_FIELDS = ["key", "roles", "why", "title"]
APPLIED_FIELDS = ["date", "key", "added", "status", "url"]

ITEMS_QUERY = """
query($owner: String!, $number: Int!, $view: Int!, $after: String) {
  organization(login: $owner) {
    projectV2(number: $number) {
      title
      view(number: $view) { name filter layout }
      items(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isArchived
          content {
            __typename
            ... on Issue {
              number title url state body
              repository { nameWithOwner }
              labels(first: 50) { nodes { name } }
              assignees(first: 10) { nodes { login } }
              milestone { title }
            }
            ... on PullRequest {
              number title url state
              repository { nameWithOwner }
              labels(first: 50) { nodes { name } }
              assignees(first: 10) { nodes { login } }
              milestone { title }
            }
            ... on DraftIssue { title }
          }
          fieldValues(first: 40) {
            nodes {
              __typename
              ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2FieldCommon { name } } }
              ... on ProjectV2ItemFieldTextValue { text field { ... on ProjectV2FieldCommon { name } } }
              ... on ProjectV2ItemFieldNumberValue { number field { ... on ProjectV2FieldCommon { name } } }
              ... on ProjectV2ItemFieldDateValue { date field { ... on ProjectV2FieldCommon { name } } }
              ... on ProjectV2ItemFieldIterationValue { title field { ... on ProjectV2FieldCommon { name } } }
            }
          }
        }
      }
    }
  }
}
"""


def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        return subprocess.run(
            ["git", "-C", here, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit(f"{here} is not inside a git checkout")


def gh(*args, check=True):
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and out.returncode:
        sys.exit(f"gh {' '.join(args[:3])} ... failed:\n{out.stderr.strip()}")
    return out


def load_json(path):
    if not os.path.exists(path):
        sys.exit(f"{path} is missing; run the earlier step first")
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def norm(s):
    return re.sub(r"[\s_-]+", "-", (s or "").strip().lower())


# --------------------------------------------------------------------------- #
# fetch
# --------------------------------------------------------------------------- #
def flatten(node):
    """One project item -> a flat dict the filter and later steps can use."""
    c = node.get("content") or {}
    kind = {"Issue": "issue", "PullRequest": "pr", "DraftIssue": "draft"}.get(
        c.get("__typename"), "unknown")
    item = {
        "kind": kind,
        "archived": node.get("isArchived", False),
        "title": c.get("title", ""),
        "number": c.get("number"),
        "url": c.get("url", ""),
        "state": (c.get("state") or "").lower(),
        "repo": (c.get("repository") or {}).get("nameWithOwner", ""),
        "labels": [l["name"] for l in (c.get("labels") or {}).get("nodes", [])],
        "assignees": [a["login"] for a in (c.get("assignees") or {}).get("nodes", [])],
        "milestone": (c.get("milestone") or {}).get("title", ""),
        "body": c.get("body", ""),
        "fields": {},
    }
    for fv in node["fieldValues"]["nodes"]:
        name = (fv.get("field") or {}).get("name")
        if not name:
            continue
        val = next((fv[k] for k in ("name", "text", "number", "date", "title")
                    if k in fv), None)
        if val is not None:
            item["fields"][norm(name)] = str(val)
    item["key"] = f"{item['repo']}#{item['number']}" if item["number"] else ""
    return item


def tokenize(expr):
    return re.findall(r'-?[\w.-]+:(?:"[^"]*"|[^\s"])+|"[^"]*"|\S+', expr or "")


def split_values(raw):
    return [v.strip('"') for v in re.findall(r'"[^"]*"|[^,]+', raw)]


def item_values(item, key):
    """Values of a filter qualifier for an item, or None if the key is unknown."""
    if key in ("label", "labels"):
        return item["labels"]
    if key == "repo":
        return [item["repo"], item["repo"].split("/")[-1]] if item["repo"] else []
    if key in ("assignee", "assignees"):
        return item["assignees"]
    if key == "milestone":
        return [item["milestone"]] if item["milestone"] else []
    if key in ("state",):
        return [item["state"]]
    if key in ("title",):
        return [item["title"]]
    if key in item["fields"]:
        return [item["fields"][key]]
    return None


def matches(item, expr, field_names):
    """Apply a GitHub Projects view filter. Unsupported syntax aborts loudly."""
    for tok in tokenize(expr):
        neg = tok.startswith("-")
        body = tok[1:] if neg else tok
        if ":" not in body or body.startswith('"'):
            ok = body.strip('"').lower() in item["title"].lower()
        else:
            key, raw = body.split(":", 1)
            key = norm(key)
            if re.match(r"^[<>]|\.\.|@", raw):
                sys.exit(f"filter token {tok!r} uses ranges or @-dates, which this "
                         "script does not evaluate; filter the scope by hand")
            vals = [v.lower() for v in split_values(raw)]
            if key == "is":
                flags = {item["kind"], item["state"],
                         "archived" if item["archived"] else "active"}
                if item["kind"] == "pr":
                    flags.add("pull-request")
                ok = any(v in flags for v in vals)
            elif key in ("no", "has"):
                present = all(item_values(item, norm(v)) for v in vals)
                ok = present if key == "has" else not any(
                    item_values(item, norm(v)) for v in vals)
            else:
                have = item_values(item, key)
                if have is None:
                    if key not in field_names:
                        sys.exit(f"filter token {tok!r}: no field named {key!r} "
                                 f"(known: {', '.join(sorted(field_names))})")
                    have = []
                have = [h.lower() for h in have]
                ok = any(fnmatch.fnmatch(h, v) for h in have for v in vals)
        if ok == neg:
            return False
    if not re.search(r"\bis:archived\b", expr or "") and item["archived"]:
        return False
    return True


def cmd_fetch(args):
    items, after, project = [], None, None
    while True:
        call = ["api", "graphql", "-f", f"query={ITEMS_QUERY}",
                "-f", f"owner={args.owner}", "-F", f"number={args.project}",
                "-F", f"view={args.view}"]
        if after:
            call += ["-f", f"after={after}"]
        out = gh(*call, check=False)
        data = json.loads(out.stdout or "{}")
        if "errors" in data or out.returncode:
            msg = (data.get("errors") or [{}])[0].get("message", out.stderr)
            if "read:project" in msg:
                msg += "\nRun: gh auth refresh -s read:project"
            sys.exit(msg)
        project = data["data"]["organization"]["projectV2"]
        page = project["items"]
        items += [flatten(n) for n in page["nodes"]]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]

    view = project["view"]
    field_names = {k for it in items for k in it["fields"]}
    in_view = [it for it in items if matches(it, view["filter"], field_names)]
    scope = [it for it in in_view if it["kind"] == "issue"]
    save_json(os.path.join(args.data_dir, "items.json"), {
        "project": project["title"], "view": view, "fetched":
        datetime.datetime.now().isoformat(timespec="seconds"), "items": items})
    save_json(os.path.join(args.data_dir, "scope.json"), {
        "project": project["title"], "view": view,
        "url": f"https://github.com/orgs/{args.owner}/projects/{args.project}/views/{args.view}",
        "not_issues": [{k: it[k] for k in ("kind", "title", "url")}
                       for it in in_view if it["kind"] != "issue"],
        "issues": scope})
    print(f"{project['title']} / view {args.view} '{view['name']}' "
          f"filter: {view['filter'] or '(none)'}")
    print(f"{len(items)} project items, {len(in_view)} in the view, "
          f"{len(scope)} issues in scope")
    already = [it for it in scope if any(l.startswith(ROLE_PREFIX) for l in it["labels"])]
    print(f"{len(already)} already carry a '{ROLE_PREFIX}' label and will be skipped")


def cmd_from_urls(args):
    """Build scope.json from a list of item URLs (when the token lacks read:project)."""
    with open(args.urls) as f:
        urls = re.findall(r"https://github\.com/[^\s]+/(?:issues|pull)/\d+", f.read())
    issues, not_issues = [], []
    for url in dict.fromkeys(urls):
        repo, kind, num = re.match(
            r"https://github\.com/([^/]+/[^/]+)/(issues|pull)/(\d+)", url).groups()
        if kind == "pull":
            not_issues.append({"kind": "pr", "title": "", "url": url})
            continue
        d = json.loads(gh("api", f"repos/{repo}/issues/{num}").stdout)
        issues.append({
            "kind": "issue", "archived": False, "title": d["title"],
            "number": int(num), "url": url, "state": d["state"], "repo": repo,
            "labels": [l["name"] for l in d["labels"]],
            "assignees": [a["login"] for a in d["assignees"]],
            "milestone": (d.get("milestone") or {}).get("title", ""),
            "body": d.get("body") or "", "fields": {}, "key": f"{repo}#{num}"})
    save_json(os.path.join(args.data_dir, "scope.json"), {
        "project": args.project_title, "url": args.view_url,
        "view": {"name": args.view_name, "filter": args.view_filter, "layout": ""},
        "not_issues": not_issues, "issues": issues})
    already = [it for it in issues if any(l.startswith(ROLE_PREFIX) for l in it["labels"])]
    print(f"{len(issues)} issues in scope, {len(not_issues)} PRs listed only; "
          f"{len(already)} already carry a '{ROLE_PREFIX}' label")


# --------------------------------------------------------------------------- #
# list / decisions
# --------------------------------------------------------------------------- #
def cmd_list(args):
    scope = load_json(os.path.join(args.data_dir, "scope.json"))["issues"]
    for it in scope[args.offset:args.offset + args.limit]:
        roles = [l for l in it["labels"] if l.startswith(ROLE_PREFIX)]
        print(f"=== {it['key']}  [{it['state']}]  {it['title']}")
        print(f"labels: {', '.join(it['labels']) or '-'}")
        if roles:
            print(f"ALREADY LABELLED: {', '.join(roles)}")
        body = re.sub(r"<!--.*?-->", "", it["body"] or "", flags=re.S)
        body = re.sub(r"\n\s*\n+", "\n", body).strip()
        print(body[:args.body] + (" ..." if len(body) > args.body else ""))
        print()


def read_decisions(data_dir):
    path = os.path.join(data_dir, "decisions.tsv")
    if not os.path.exists(path):
        sys.exit(f"{path} is missing; write one row per issue: "
                 f"{chr(9).join(DECISION_FIELDS)}")
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def validate(data_dir):
    scope = {it["key"]: it for it in
             load_json(os.path.join(data_dir, "scope.json"))["issues"]}
    rows, problems = read_decisions(data_dir), []
    seen = set()
    for r in rows:
        key = r["key"].strip()
        if key not in scope:
            problems.append(f"{key}: not in scope")
        if key in seen:
            problems.append(f"{key}: listed twice")
        seen.add(key)
        roles = [x.strip() for x in r["roles"].split(",") if x.strip()]
        bad = [x for x in roles if x not in ROLE_LABELS]
        if bad:
            problems.append(f"{key}: unknown role(s) {bad}; use {sorted(ROLE_LABELS)}")
        if not roles:
            problems.append(f"{key}: no roles")
        if not r.get("why", "").strip():
            problems.append(f"{key}: missing why")
    missing = [k for k, it in scope.items() if k not in seen
               and not any(l.startswith(ROLE_PREFIX) for l in it["labels"])]
    problems += [f"{k}: unlabelled and has no decision" for k in missing]
    return scope, rows, problems


def cmd_check(args):
    _, rows, problems = validate(args.data_dir)
    for p in problems:
        print(p)
    print(f"{len(rows)} decisions, {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


# --------------------------------------------------------------------------- #
# apply
# --------------------------------------------------------------------------- #
def repo_labels(repo, cache={}):
    if repo not in cache:
        out = gh("label", "list", "-R", repo, "-L", "1000", "--json", "name")
        cache[repo] = {l["name"] for l in json.loads(out.stdout)}
    return cache[repo]


def cmd_apply(args):
    scope, rows, problems = validate(args.data_dir)
    if problems:
        sys.exit("decisions.tsv has problems; run `check` and fix them first")
    log_path = os.path.join(args.data_dir, "applied.tsv")
    new_log = not os.path.exists(log_path)
    log = open(log_path, "a", newline="") if args.yes else None
    writer = csv.DictWriter(log, APPLIED_FIELDS, delimiter="\t") if log else None
    if writer and new_log:
        writer.writeheader()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    for r in rows:
        it = scope[r["key"].strip()]
        want = [ROLE_LABELS[x.strip()] for x in r["roles"].split(",") if x.strip()]
        missing = [l for l in want if l not in repo_labels(it["repo"])]
        # re-read live labels: someone may have classified it since the fetch
        live = json.loads(gh("api", f"repos/{it['repo']}/issues/{it['number']}",
                             "--jq", "[.labels[].name]").stdout)
        existing = [l for l in live if l.startswith(ROLE_PREFIX)]
        if missing:
            # never create labels; report the gap instead
            status, added = "skipped: repo has no " + ", ".join(missing), []
        elif existing:
            status, added = "skipped: already has " + ", ".join(existing), []
        else:
            added = want
            status = "added" if args.yes else "would add"
            if args.yes:
                call = ["api", "-X", "POST",
                        f"repos/{it['repo']}/issues/{it['number']}/labels"]
                for l in added:
                    call += ["-f", f"labels[]={l}"]
                gh(*call)
        print(f"{status:<12} {it['key']:<32} {', '.join(added or existing)}")
        if writer:
            writer.writerow({"date": now, "key": it["key"], "added": "; ".join(added),
                             "status": status, "url": it["url"]})
    if log:
        log.close()
    if not args.yes:
        print("\nDry run. Re-run with --yes to add the labels.")


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #
def md(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def cmd_report(args):
    sc = load_json(os.path.join(args.data_dir, "scope.json"))
    scope = {it["key"]: it for it in sc["issues"]}
    decisions = {r["key"].strip(): r for r in read_decisions(args.data_dir)}
    applied = {}
    path = os.path.join(args.data_dir, "applied.tsv")
    if os.path.exists(path):
        with open(path, newline="") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                applied[r["key"]] = r  # last run wins
    added = [k for k, a in applied.items() if a["status"] == "added"]
    no_label = [k for k, a in applied.items()
                if a["status"].startswith("skipped: repo has no")]
    skipped = [k for k, a in applied.items()
               if a["status"].startswith("skipped") and k not in no_label]
    pre = [k for k, it in scope.items() if k not in decisions
           and any(l.startswith(ROLE_PREFIX) for l in it["labels"])]

    counts = {r: 0 for r in ROLE_LABELS}
    for k in added:
        for x in decisions[k]["roles"].split(","):
            counts[x.strip()] += 1

    out = [f"# User-role labelling report",
           "",
           f"- **View:** [{sc['project']} / {sc['view']['name']}]({sc['url']})",
           f"- **View filter:** `{sc['view']['filter'] or '(none)'}`",
           f"- **Generated:** {datetime.datetime.now().isoformat(timespec='minutes')}",
           f"- **Issues in scope:** {len(scope)} "
           f"(plus {len(sc['not_issues'])} PRs/drafts in the view, not labelled)",
           f"- **Labelled now:** {len(added)}",
           f"- **Left alone (already had a `{ROLE_PREFIX}` label):** "
           f"{len(pre) + len(skipped)}",
           "",
           "## Labels added by category",
           "",
           "| Category | Label | Issues |",
           "| --- | --- | --- |"]
    out += [f"| {ROLE_NAMES[r]} | `{ROLE_LABELS[r]}` | {counts[r]} |" for r in ROLE_LABELS]
    out += ["", "## Issues labelled", "",
            "| Issue | Title | Labels added | Why |", "| --- | --- | --- | --- |"]
    for k in added:
        it, d = scope[k], decisions[k]
        out.append(f"| [{k}]({it['url']}) | {md(it['title'])} | "
                   f"{md(applied[k]['added'])} | {md(d['why'])} |")
    if pre or skipped:
        out += ["", "## Left alone", "",
                "| Issue | Title | Existing role labels |", "| --- | --- | --- |"]
        for k in pre:
            it = scope[k]
            out.append(f"| [{k}]({it['url']}) | {md(it['title'])} | "
                       f"{', '.join(l for l in it['labels'] if l.startswith(ROLE_PREFIX))} |")
        for k in skipped:
            out.append(f"| [{k}]({scope[k]['url']}) | {md(scope[k]['title'])} | "
                       f"{applied[k]['status'].split(': ', 1)[-1]} |")
    if no_label:
        out += ["", "## Classified but not labelled (repo lacks the label)", "",
                "| Issue | Title | Classified as | Why |", "| --- | --- | --- | --- |"]
        for k in no_label:
            roles = ", ".join(ROLE_NAMES[x.strip()]
                              for x in decisions[k]["roles"].split(","))
            out.append(f"| [{k}]({scope[k]['url']}) | {md(scope[k]['title'])} | "
                       f"{roles} | {md(decisions[k]['why'])} |")
    pending = [k for k in decisions if k not in applied]
    if pending:
        out += ["", "## Decided but not applied", ""]
        out += [f"- [{k}]({scope[k]['url']}) {md(scope[k]['title'])}: "
                f"{decisions[k]['roles']}" for k in pending if k in scope]
    if sc["not_issues"]:
        out += ["", "## Not issues (not labelled)", ""]
        out += [f"- {n['kind']}: {md(n['title'])} {n['url']}" for n in sc["not_issues"]]
    text = "\n".join(out) + "\n"
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    dest = os.path.join(args.data_dir, f"report-{stamp}.md")
    with open(dest, "w") as f:
        f.write(text)
    print(text)
    print(f"(saved to {dest})")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir",
                   default=os.path.join(repo_root(), "automation", "user-roles"))
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--owner", default="IQSS")
    f.add_argument("--project", type=int, default=34)
    f.add_argument("--view", type=int, default=52)
    u = sub.add_parser("from-urls", help="build the scope from a file of item URLs")
    u.add_argument("urls")
    u.add_argument("--project-title", default="IQSS Dataverse Project")
    u.add_argument("--view-name", default="")
    u.add_argument("--view-filter", default="")
    u.add_argument("--view-url", default="")
    l = sub.add_parser("list")
    l.add_argument("--offset", type=int, default=0)
    l.add_argument("--limit", type=int, default=1000)
    l.add_argument("--body", type=int, default=1200, help="body chars to show")
    sub.add_parser("check")
    a = sub.add_parser("apply")
    a.add_argument("--yes", action="store_true", help="add the labels on GitHub")
    sub.add_parser("report")
    args = p.parse_args()
    os.makedirs(args.data_dir, exist_ok=True)
    {"fetch": cmd_fetch, "from-urls": cmd_from_urls, "list": cmd_list, "check": cmd_check,
     "apply": cmd_apply, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()
