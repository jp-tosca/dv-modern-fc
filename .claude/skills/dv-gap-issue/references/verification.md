# Verifying an item: local environment, source lookup, evidence

## Local environment

Checked on 2026-09-16; re-check at the start of every session, because the ports
move when the dev servers are restarted:

```bash
curl -s -o /dev/null -w "legacy:%{http_code}\n" http://localhost:8080/
curl -s -o /dev/null -w "modern:%{http_code}\n" http://localhost:8000/modern
```

| What | Where |
| --- | --- |
| Legacy JSF UI | http://localhost:8080/ |
| New frontend (Vite dev server) | http://localhost:8000/modern |
| Login | `dataverseAdmin` / `admin1` (superuser) |
| Legacy source clone | `/Users/jptosca/REP/IQSS/dataverse` |
| Frontend source clone | `/Users/jptosca/REP/IQSS/dataverse-frontend` |

The modern frontend is *not* served from port 8080 — a request to
`http://localhost:8080/modern` returns the JSF 404 page. If either probe fails,
stop and tell the user which server is down instead of concluding that a feature
is missing; an unreachable SPA looks exactly like a missing route.

The local clones may sit on a feature branch (`git -C <clone> rev-parse
--abbrev-ref HEAD`), so use them for searching but write issue links against the
upstream default branch, which is `develop` in both repositories.

## Finding the legacy implementation

The missing-items row already names likely files in its *JSF Implementation
Reference* column — treat that as a starting hypothesis and confirm it.

1. JSF labels come from the resource bundle, so the fastest route from a UI label
   to the code is the bundle:
   ```bash
   grep -n "Save Linked Search" /Users/jptosca/REP/IQSS/dataverse/src/main/java/propertyFiles/Bundle.properties
   # -> dataverse.savedsearch.save=Save Linked Search
   grep -rn "dataverse.savedsearch.save" /Users/jptosca/REP/IQSS/dataverse/src/main/webapp
   ```
2. From the `.xhtml` page, follow the `action`/`actionListener`/`rendered`
   expressions into the backing bean under
   `src/main/java/edu/harvard/iq/dataverse/`. The `rendered` condition usually
   tells you the prerequisites (superuser, publish state, permission, feature
   flag) you need to satisfy to see the control at all.
3. Note the permission/state prerequisites in the issue's steps — several items
   only appear for superusers, for published datasets, or when an optional
   integration (Globus, compute, external tools) is configured. A control that is
   invisible locally because the install lacks Globus is *not reproducible* here,
   not confirmed missing.

## Finding the frontend implementation (or its absence)

```bash
cd /Users/jptosca/REP/IQSS/dataverse-frontend
grep -rn "Link Search" public/locales/en/          # UI strings live in i18n JSON
grep -rn "savedSearch\|linkSearch" src/ --include="*.ts*"
sed -n '1,200p' src/sections/Route.enum.ts          # what routes exist at all
grep -rln "NotImplementedModal" src/sections        # where placeholders are wired
```

The three outcomes to distinguish, because they need different issue wording:

- **Absent** — no menu entry, no route, no i18n string. Nothing to click.
- **Stubbed** — the control exists but calls `NotImplementedModal` (common across
  `src/sections/collection/edit-collection-dropdown/`,
  `src/sections/dataset/dataset-action-buttons/`).
- **Partial / divergent** — the workflow exists but drops fields, permissions or
  states that legacy supports. Say exactly which.

Confirm the outcome in the browser as well as in the source. The SPA hides many
controls behind permissions and publish state, so source-only reasoning produces
false "absent" claims.

## Browser work (Claude Chrome plugin only)

Use the Claude Chrome plugin tools for every page interaction, login, and
screenshot. The built-in `WebFetch` cannot reach `localhost` and cannot log in,
and `curl` output is not acceptable evidence for a UI gap. If the plugin's tools
are not available in the session, say so and stop — do not substitute another
browser tool or file an issue from source reading alone.

Practical notes:

- Log into both apps once at the start of a session; the two run on different
  ports and therefore hold separate sessions.
- Use the same collection/dataset in both apps so the screenshots compare like
  with like. Prefer existing sample data; create test data only when the feature
  needs a state that does not exist yet.
- Keep the window size consistent between the two screenshots.

## Test data and the API

The install allows disposable test data. Creating it through the API is usually
faster and less error-prone than clicking through the legacy UI:

```bash
curl -H "X-Dataverse-key: $TOKEN" http://localhost:8080/api/dataverses/root
```

`/api/builtin-users/dataverseAdmin/api-token` is disabled on this install, so get
the token from the legacy UI once per session (Account -> API Token) and keep it
in the scratchpad rather than in the repository.

Boundaries: create or modify only data you created for the reproduction, and note
it in the final report. Do not delete or edit unrelated collections, datasets or
users, do not change install-wide settings (`/api/admin/settings/...`), and do not
touch source code, repository configuration, or anything in the upstream GitHub
repositories.

## Screenshots

Save both screenshots to `automation/screenshots/` with a name that ties them to
the list index, so a reviewer can find the pair later:

```
automation/screenshots/012-dataset-thumbnail-legacy.png
automation/screenshots/012-dataset-thumbnail-modern.png
```

Each pair must show the *same* thing: legacy showing the feature working, modern
showing its absence, stub or divergence. When the difference is not visually
obvious (a missing item inside a long dropdown, a field absent from a form),
annotate the image or write a caption that points at the exact region — "Link
dropdown expanded; legacy lists Link Search, modern lists only Link Collection".

## Attaching screenshots to the issue

GitHub renders attachments as `user-attachments` URLs, and those only exist once
a file has been uploaded through the web form — `gh issue create` cannot upload
images. So compose the issue in the GitHub web UI via the Chrome plugin: open
`https://github.com/jp-tosca/dv-modern-fc/issues/new`, paste the title and body,
then attach each PNG with the form's file input (the "paste, drop, or click to add
files" control) at the right place in the body.

If the upload cannot be completed through the plugin, do not silently file an
issue with no evidence and do not link to local file paths. Either leave the
issue as a draft and ask the user to drop the two PNGs into the form, or file it
and immediately add the screenshots in a follow-up comment — and say which you
did in the progress record.
