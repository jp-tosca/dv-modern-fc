# Gaps Identified by the AI Inventories but Missing from the Human Roadmap

## Method

Four documents were compared:

1. `jsf-feature-inventory-MODEL 1.tsv` — AI inventory of legacy JSF functionality (483 items).
2. `jsf-functionality-inventory - MODEL 2.tsv` — a second, independently-produced AI inventory (244 items, different page/granularity scheme).
3. `DV - Functionality inventory - dataverse-frontend implementation status.tsv` — an AI pass that took Model 1's inventory (same 483 rows, same Page/Functionality columns) and added an "Implemented in dataverse-frontend" verdict (`Yes` / `Partial` / `No`) plus evidence.
4. `features-remaining-roadmap.md` — the human-written list of what's left to build.

**Important finding on the source data itself:** the implementation-status file was built only from Model 1's list. Model 2 was never reconciled against it, so anything Model 2 caught that Model 1 phrased differently or omitted got no implementation verdict at all — it's a blind spot in the AI-assisted step too, not just the human one. Where Model 2 independently corroborates a gap below, it's noted.

There are ~150 rows marked `No` and ~45 marked `Partial` in the implementation-status file. The human roadmap has 17 bullets in scope plus 7 flagged "to consider." Below are the AI-flagged gaps that don't map to *any* bullet in either section of the roadmap — i.e., functionality that would currently surprise someone expecting JSF-equivalent behavior in the new frontend, with no corresponding line item anywhere in the roadmap doc.

Items that already map cleanly to the roadmap (e.g. all the `Manage Permissions` / `Manage File Permissions` / `Manage Groups` rows → "Collection — Permissions/Groups"; `Preview URL` rows → "Dataset — Preview URLs"; `Theme & Widgets` → "Branding"; `Change Curation Status`/`Submit for Review` → "Review Workflow"; `External Controlled-Vocabulary Lookup` → "External Controlled Vocabulary"; `View Dataset Citations Count` → "Add Views and Citations to Dataset Metrics Component") are **excluded** — those were already caught by the human.

## Whole feature areas missing from the roadmap

These are entire subsystems the AI inventories flagged as absent/partial, with no mention anywhere in `features-remaining-roadmap.md` (main list or "to consider" list).

| Feature area | Status | Corroborated by Model 2? | Representative rows (impl-status file) |
|---|---|---|---|
| **Compute** (external compute-on-data integration) | No | Yes (Compute rows present) | Add/Remove/Clear/View Compute Cart, Compute Dataset, Run Compute Batch, Compute on File, Compute Access Denied Notice, Compute Restricted-File Warning |
| **Globus integration** | No | Yes | Globus Transfer Dataset, Batch Globus Transfer, Upload Files via Globus, File Access & Download → Globus Transfer |
| **Alternate/advanced upload channels** — the roadmap only lists "Upload Files via Local" | No | Yes (Dropbox/rsync/template rows present) | Upload Files via Dropbox, Upload Files via Webloader, Download Rsync Upload Script, Advanced Ingest Options (Encoding), Resolve Duplicate/Type-Mismatch Upload, Upload SPSS-POR Extra Labels File |
| **File Provenance** (entire tab) | No | Yes (11 rows) | Upload/View/Preview/Remove Provenance JSON, View Provenance Graph, Toggle Ancestors/Successors, Select Provenance Entity |
| **Guestbooks** (entire subsystem) | No | Yes (21 rows) | Manage Guestbooks (create/edit/delete), Guestbook Response Form, Guestbook Preview Dialog, Guestbook Terms & Download Dialog |
| **Templates** (metadata templates) | No | Yes (13 rows) | Manage Templates, Make/Unset Default Template, Template Create/Edit |
| **Dataset Thumbnails & Widgets** (per-dataset thumbnail + embed code — distinct from site-wide Branding/Theme) | No | Yes (5 rows) | Select/Upload/Remove Dataset Thumbnail, Save Thumbnail Changes, View Widget Embed Code |
| **DataTags** deposit tool | No | Yes | Submit Dataset Name for DataTags Interview, DataTags Deposit Complete (Test Display) |
| **Dataset archiving** | No | Model 1 only | Submit Version for Archiving, View Archival Copy Status |
| **File retention periods** — distinct from Embargo, which *is* on the roadmap | No | Yes (3 rows) | Set/Remove Retention Period |
| **File ingest/uningest controls** | No | Model 1 only | Ingest File, Uningest File |
| **Rsync-based data access** (separate from the upload-side rsync item above) | No | Model 1 only | View Rsync Access Instructions, Rsync Data Access Popup |
| **Search index administration** | No | Yes (2 rows) | Check Status of Index All, Index All (superuser reindex) |
| **Account Information self-service editing** — roadmap only names "verify email" | No | Yes (6 rows) | Change Password, Edit Account Information, Save Account Changes, Link/Remove ORCID iD, Save New Password |
| **Package / multi-file download** | No | Model 1 only | Download Package (Multi-file Bundle), Package Download Popup (view package info) |
| **Notification preferences** | No | Model 1 only | Manage Muted Email Notifications, Manage Muted In-App Notifications |

## Smaller/secondary gaps also unmentioned

Lower-impact items, individually minor but not covered anywhere in the roadmap:

- **Auxiliary file download** (`File Access & Download → Download Auxiliary File`)
- **Role/Permission matrix viewer** (`Role Permission Helper → View Role/Permission Matrix`)
- **"Contact Support" links** missing/partial across Login Page, Account Information, ORCID Confirmation, OAuth Callback, Search Results (no-results guidance) — a recurring UI affordance, flagged repeatedly by both inventories, not a one-off
- **Metadata language selection** and **Replication Data prefix** (`Dataset Metadata`)
- **Citation style switcher** — "Cite Dataset in Multiple Styles" (Partial)
- **404 static fallback page** (distinct from the dynamic 403/404/500 error pages)
- **My Data — Filter by Metadata Validity**
- **OAuth/Shibboleth account conversion detail flows** (Cancel/Convert Existing Account) — tangential to the roadmap's "Account Registration integration" bullet, but that bullet reads as new-signup only; the *conversion* path for existing accounts isn't clearly in scope of it

## Not actually gaps (already covered, for reference)

Confirmed these AI-flagged items **do** map to an existing roadmap bullet, so they're correctly excluded above:

- All `Manage Permissions`, `Manage File Permissions`, `Manage Groups`, `Dataverse Page` permission/group shortcuts → "Collection — Permissions / Groups"
- `Dataverse Page → Save Linked Search` → "Collection — Link Search"
- `Preview URL` rows → "Dataset — Preview URLs"
- `Dataset Files Tab → Toggle Table/Tree View` → "Dataset — Files Tree View"
- `Edit Files (Upload)` local-upload path → "Dataset — Upload Files via Local" (though see the "alternate upload channels" gap above — only the local path is covered)
- `File Edit Options → Set/Remove Embargo` → "File — Embargo"
- `Confirm Email` → "Account — verify email"
- `Manage Users` → "Dashboard — Manage Users"
- `Harvesting Clients`, `Harvesting Sets` → "Dashboard — Harvesting Clients / Harvesting Server"
- `Move Dataset`, `Move Dataverse (Dashboard)` → "Dashboard — Move Dataset & Move Dataverse"
- `Theme & Widgets` → "Branding"
- `Dataset Page → Change/Remove Curation Status`, `Submit Dataset for Review` → "Review Workflow"
- `Dataset Metadata → Use External Controlled-Vocabulary Lookup` → "External Controlled Vocabulary"
- `Dataset Page → View Dataset Citations Count` → "Add Views and Citations to Dataset Metrics Component"

## Bottom line

The human roadmap correctly captures the "big obvious" missing sections (permissions, groups, harvesting, move tools, branding) but misses several **entire subsystems** that both AI inventories independently flagged: **Compute**, **Globus**, **Provenance**, **Guestbooks**, **Templates**, **dataset-level Thumbnails/Widgets**, **DataTags**, **archiving**, **retention periods**, and **self-service account editing**. Guestbooks, Templates, and Provenance in particular are large enough (13–21 rows each) that they read as oversights rather than deliberate deferrals — worth confirming with the team whether they're intentionally out of scope or simply not yet catalogued.
