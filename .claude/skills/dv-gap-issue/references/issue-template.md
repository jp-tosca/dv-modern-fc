# Issue template and writing guide

Every issue filed by this skill uses the same body structure. Consistency matters
here because the issues are read as a set — a maintainer skimming twenty of them
should be able to find "what's missing" and "how do I see it" in the same place
every time.

## Title

Name the feature and the observed gap, from the reader's point of view. The title
should make sense to someone who has never seen `DV - Missing items.md`.

Good:
- `Collection page missing Save Linked Search (Link Search) action`
- `Collection "Manage Groups" shortcut opens placeholder instead of groups page`
- `Site-wide dismissible banner messages are not rendered in the new frontend`

Bad: `Missing feature`, `Save Linked Search`, `Dataverse Page gap #12`.

Where the new frontend shows a "Not Implemented" placeholder, say so in the title —
that distinction (absent vs. stubbed) is the first thing a maintainer wants to know.

## Body

```markdown
## Summary

Briefly explain the feature and why it matters.

## Legacy JSF behavior

Describe how the feature works in the legacy interface.

### Steps to observe

1. ...
2. ...
3. ...

## New frontend behavior

Describe what happens when attempting the equivalent workflow in the new frontend.

### Steps to reproduce

1. ...
2. ...
3. ...

## Expected behavior

Describe the behavior the new frontend should support.

## Current behavior

Describe precisely what is missing, incomplete, inaccessible, or inconsistent.

## Evidence

### Legacy JSF

Attach the screenshot and add a short caption.

### New frontend

Attach the corresponding screenshot and add a short caption.

## Implementation references

- Legacy JSF source: link to relevant files or lines when available.
- New frontend source: link to relevant files or components when available.
- Missing-items entry: link to the corresponding section of `DV - Missing items.md`.

## Related issues

- List relevant open, closed, or completed issues.
- State how each issue relates to this one.
- Write "None found" if the searches did not find any.

## Acceptance criteria

- [ ] ...
- [ ] ...
- [ ] ...
```

Notes per section:

- **Steps to observe / reproduce** — write the steps actually walked in the browser,
  including the login and the specific collection/dataset used. Someone should be
  able to replay them on a fresh local install. Start with the URL
  (`http://localhost:8080` for legacy, `http://localhost:8000/modern` for the SPA).
- **Current behavior** — be exact about the failure mode: menu entry absent, entry
  present but opens the "Not Implemented" modal, route 404s, action succeeds but
  drops a field, etc. This is the sentence a maintainer will quote back.
- **Implementation references** — prefer permalinks to the upstream default branch
  (`develop` in both `IQSS/dataverse` and `IQSS/dataverse-frontend`), e.g.
  `https://github.com/IQSS/dataverse/blob/develop/src/main/webapp/dataverse.xhtml`.
  If nothing was found on the frontend side, say that plainly ("no matching
  route/component found under `src/router/routes.tsx` or `src/sections`") rather
  than omitting the bullet.
- **Related issues** — one bullet per issue, each ending in how it relates
  ("discusses X but does not cover Y — not a duplicate"). If the searches came up
  empty, say which terms were searched, so the next reader knows the coverage.
- **Acceptance criteria** — derive them from the legacy behavior just observed, one
  checkbox per user-visible capability, plus one for test coverage. Avoid
  implementation prescriptions (which component, which hook); the maintainers own
  that decision.

## Reference example

`jp-tosca/dv-modern-fc#1` ("Collection page missing Save Linked Search (Link
Search) action") is the worked example for tone, length and level of detail. Read
it with `gh issue view 1 -R jp-tosca/dv-modern-fc` before writing the first issue
of a session. Issues #2 and #3 are the pattern for the "opens the Not Implemented
placeholder" variant, and #4 for a feature that renders nothing at all.

## Repository conventions

`jp-tosca/dv-modern-fc` only has GitHub's stock labels and no milestones, and
issues #1-#4 carry no labels, assignees or milestone. Follow that: create issues
with a title and body only. If the repository later grows a real labeling
convention, adopt it then.
