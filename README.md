# dv-modern-fc

Tracking and reporting on feature-completion status for the Modern Dataverse frontend (the React SPA rewrite of the legacy JSF UI).

## Background

Before this repository existed, Ellen compiled a baseline list of features to be replicated, available in Google Docs and mirrored here in [features-remaining-roadmap.md](features-remaining-roadmap.md).

This repository extends that baseline with AI-generated inventories that cross-reference legacy JSF functionality against the current SPA implementation.

## Methodology

1. **Inventory the legacy JSF frontend.** Two AI coding tools independently analyzed the Dataverse codebase to catalog the functionality implemented in the JSF frontend:
   - [jsf-feature-inventory-MODEL 1.md](jsf-feature-inventory-MODEL%201.md)
   - [jsf-functionality-inventory - MODEL 2.md](jsf-functionality-inventory%20-%20MODEL%202.md)

2. **Check implementation status against the SPA.** Using the Model 1 inventory as input, another AI tool checked each JSF feature against the SPA codebase to determine whether it has been implemented, partially implemented, or is still missing. The results are in [Inventory check with SPA.md](Inventory%20check%20with%20SPA.md).

3. **Isolate the gaps.** The features not yet implemented in the SPA are filtered into [DV - Missing items.md](DV%20-%20Missing%20items.md) for quick reference.

Each inventory table includes the page, functionality name, a description, implementation status, supporting evidence (route/component/use-case references), and any relevant notes.

## Directory structure

- `data/` — source TSV exports backing the Markdown tables above.
- `*.md` — human-readable inventories and reports described in [Methodology](#methodology).

## Caveats

These inventories were produced by AI tools and should be treated as a starting point rather than a ground truth. Entries marked "No SPA route/component/use-case found" reflect the tool's search of the codebase at the time of analysis and may need manual verification before being used to prioritize work.
