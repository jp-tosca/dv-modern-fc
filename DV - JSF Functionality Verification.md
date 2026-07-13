# Dataverse JSF Web Application — Functionality Verification & Location Guide

## Purpose

The companion document [`DV - Missing items.txt`](./DV%20-%20Missing%20items.txt) lists 231 pieces of functionality present in the classic **JSF web application** (this repository, `src/main/webapp/*.xhtml`) that were found missing or only partially implemented in the new React SPA rewrite (`dataverse-frontend`). This document does the reverse validation: it confirms that each item **actually exists in the JSF app**, and tells you exactly which page/fragment implements it and how to reach it from the UI.

## Methodology & caveats

- Verification was done by static analysis of the JSF markup (`.xhtml`) and, where needed, the corresponding backing beans (`src/main/java`) — grepping for the button/tab/dialog/menu item described, and confirming it's wired to a real action/listener. This is strong evidence the feature is implemented in code, but it is **not** a live click-through of a running instance.
- Several items are optional or config/feature-flag gated (Globus transfer, Dropbox upload, DCM/rsync upload, external compute tools, archiving via DuraCloud/Chronopolis). These are marked ✅ **Yes** because the UI and backing logic exist in the codebase, but they will only be visible in a running instance if the corresponding setting is enabled.
- Fragments (`*-fragment.xhtml`) are not stand‑alone pages — they are pulled into a parent page via `<ui:include>`. The "JSF Page(s)" column lists the fragment plus, where relevant, the page(s) that include it.
- Status legend: **Yes** = confirmed present and wired to real behavior · **Partial** = present but with a caveat noted in Evidence.

## Result summary

- **231** functionality items checked
- **229** confirmed **Yes**
- **2** confirmed **Partial** (row 139 "View Role/Permission Matrix" — page exists but no in-app menu link found to it; row 230 "Contact Support (No Results Guidance)" — no-results banner has guidance links but no dedicated Contact Support action)
- **0** Not Found

---

## Dataverse Page

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 2 | Save Linked Search | `dataverse.xhtml` | Dataverse page → edit menu (linking icon) → "Link/Save Search" popup | Yes | `dataverse.xhtml:550` `setupLinkingPopup('savedSearch')`, `:821` `saveSavedSearch` |
| 3 | Manage Permissions Shortcut | `dataverse.xhtml`, `permissions-manage.xhtml` | Dataverse page → Edit dropdown → "Permissions" link | Yes | `dataverse.xhtml:591` `<h:link id="managePermissions" outcome="permissions-manage">` |
| 4 | Manage Groups Shortcut | `dataverse.xhtml`, `manage-groups.xhtml` | Dataverse page → Edit dropdown → "Groups" link | Yes | `dataverse.xhtml:599` `<h:link id="manageGroups" outcome="manage-groups">` |
| 183 | Select Host (Parent) Dataverse | `dataverse.xhtml` | New Dataverse form → "Host Dataverse" field | Yes | `dataverse.xhtml:77` `p:autoComplete id="selectHostDataverse"` |
| 184 | Reset Metadata to Inherited | `dataverse.xhtml` | Dataverse edit → Metadata Elements panel → reset-to-inherit button | Yes | `dataverse.xhtml:346-350` `p:commandButton id="resetToInherit" action="#{DataversePage.resetToInherit()}"` |
| 185 | Blocked Publish Notice | `dataverse.xhtml` | Dataverse page → click Publish when parent unpublished | Yes | `dataverse.xhtml:717-723` `p:dialog id="mayNotRelease"` |
| 186 | View Root Dataverse Download Metrics | `dataverse.xhtml` | Root dataverse page → "Metrics" stat box | Yes | `dataverse.xhtml:481-497` `id="metrics-block1"` links to `settingsWrapper.metricsUrl` |

## Dataverse Homepage

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 187 | View Custom Root Homepage | `dataverse_homepage.xhtml` | Visiting the site root URL | Yes | `dataverse_homepage.xhtml:26` `o:resourceInclude ... customFileType=homePage` |

## Site Header

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 5 | Dismiss Banner Message | `dataverse_header.xhtml` | Site-wide banner alert → close (×) button | Yes | `dataverse_header.xhtml:206` `closeButton` → `dataverseSession.dismissMessage(message)` |
| 6 | Go to Dashboard | `dataverse_header.xhtml` | Header user menu (superuser) → "Dashboard" link | Yes | `dataverse_header.xhtml:172-175` rendered if `dataverseSession.user.superuser`, links to `dashboard.xhtml` |
| 188 | Sign Up | `dataverse_header.xhtml` | Header top-right "Sign Up" link | Yes | `dataverse_header.xhtml:114-116` `outputLink rendered="#{dataverseHeaderFragment.signupAllowed}"` |

## Theme & Widgets

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 7 | View Theme Tab | `ThemeAndWidgets.xhtml`, `themeAndWidgetsFragment.xhtml` | Dataverse page → Edit → Theme + Widgets → Theme tab | Yes | `themeAndWidgetsFragment.xhtml:10` `p:tab id="themeTab"` |
| 8 | Toggle Inherit Theme from Parent | `themeAndWidgetsFragment.xhtml` | Theme tab → "Inherit Theme" checkbox | Yes | `:26-28` `inheritCustomization` checkbox, `checkboxListener()` |
| 9 | Upload/Change Logo | `themeAndWidgetsFragment.xhtml` | Theme tab → Logo Image → upload/change control | Yes | `:53-58` `p:fileUpload id="changelogo"/"uploadlogo"` |
| 10 | Remove Logo | `themeAndWidgetsFragment.xhtml` | Theme tab → Logo Image → "Remove" button | Yes | `:51` `action="#{themeWidgetFragment.removeLogo()}"` |
| 11 | Set Logo Format & Alignment | `themeAndWidgetsFragment.xhtml` | Theme tab → Logo Format (Square/Rectangle), Alignment, Background Color | Yes | `:68-99` `logoFormat`, `logoAlignment`, `logoBackgroundColor` |
| 12 | Upload/Remove Logo Thumbnail | `themeAndWidgetsFragment.xhtml` | Theme tab → Logo Thumbnail section | Yes | `:121-128` `removeLogoThumbnail()`, `changelogothumbnail` upload |
| 13 | Set Header Colors | `themeAndWidgetsFragment.xhtml` | Theme tab → Header Color (background/link/text pickers) | Yes | `:149-171` `backgroundColor`, `linkColor`, `textColor` colorPickers |
| 14 | Edit Tagline | `themeAndWidgetsFragment.xhtml` | Theme tab → Tagline text field | Yes | `:190` `p:inputText id="tagline"` |
| 15 | Edit Website Link | `themeAndWidgetsFragment.xhtml` | Theme tab → Website URL field | Yes | `:202` `p:inputText id="website"` |
| 16 | Upload/Remove Footer Logo | `themeAndWidgetsFragment.xhtml` | Theme tab → Footer Logo section | Yes | `:222-229` `removeLogoFooter()`, `changelogoFooter` upload |
| 17 | Save Theme Changes | `themeAndWidgetsFragment.xhtml` | Theme tab → "Save Changes" button | Yes | `:265` `action="#{themeWidgetFragment.save()}"` |
| 18 | Cancel Theme Edit | `themeAndWidgetsFragment.xhtml` | Theme tab → "Cancel" button | Yes | `:266` `id="themeCancel" action="#{themeWidgetFragment.cancel()}"` |
| 19 | View Widget Embed Code | `themeAndWidgetsFragment.xhtml` | Theme + Widgets → Widgets tab → embed code textareas | Yes | `:275-326` `p:tab id="widgetsTab"`, search/iframe script textareas |

## Dataset Thumbnails & Widgets

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 20 | Upload Dataset Thumbnail | `dataset-widgets.xhtml` | Dataset page → Edit → Thumbnails + Widgets → upload control | Yes | `:76-80` `p:fileUpload` listener `handleImageFileUpload` |
| 21 | Remove Dataset Thumbnail | `dataset-widgets.xhtml` | Thumbnails tab → "Remove" (confirm dialog if derived from a data file) | Yes | `:49,149-155` `flagDatasetThumbnailForRemoval()`, `confrmRemove` dialog |
| 22 | Select File as Thumbnail | `dataset-widgets.xhtml` | Thumbnails tab → "Select Available File" button/dialog | Yes | `:65-66,162-183` `selectFileThumbnail` dialog, `setDataFileAsThumbnail()` |
| 23 | Save Thumbnail Changes | `dataset-widgets.xhtml` | Thumbnails tab → "Save Changes" button | Yes | `:86` `action="#{DatasetWidgetsPage.save()}"` |
| 24 | Cancel Thumbnail Edit | `dataset-widgets.xhtml` | Thumbnails tab → "Cancel" button | Yes | `:87` `action="#{DatasetWidgetsPage.cancel()}"` |
| 25 | View Widget Embed Code | `dataset-widgets.xhtml` | Dataset page → Widgets tab → citation/full-display embed textareas | Yes | `:126-140` citation/datasetFull textareas |

## Move Dataverse (Dashboard)

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 26 | Select Dataverse to Move | `dashboard-movedataverse.xhtml` | Dashboard → Move Dataverse → source dataverse autocomplete | Yes | `:39-61` `sourceDataverseMenu` `p:autoComplete` |
| 27 | Select Destination Dataverse | `dashboard-movedataverse.xhtml` | Move Dataverse → destination dataverse autocomplete | Yes | `:80-102` `destinationDataverseMenu` `p:autoComplete` |
| 28 | Submit Move Request | `dashboard-movedataverse.xhtml` | Move Dataverse page → "Save Changes" opens confirm dialog | Yes | `:112-119` `id="move"` shows `moveDataverseConfirmation` |
| 29 | Confirm Move Dataverse | `dashboard-movedataverse.xhtml` | Move Dataverse → confirm dialog → "Yes" | Yes | `:126-129` `action="#{DashboardMoveDataversePage.move()}"` |
| 30 | Cancel Move | `dashboard-movedataverse.xhtml` | Move Dataverse page → "Cancel" button | Yes | `:120` `p:button outcome="dashboard" value="cancel"` |

## Dataset Page

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 31 | Globus Transfer Dataset | `dataset.xhtml` | Access Dataset dropdown → Globus transfer option (when `versionHasGlobus`) | Yes | `:274-277` `actionListener="#{DatasetPage.startGlobusTransfer(true,false)}"` |
| 32 | Compute Dataset (Single) | `dataset.xhtml` | Access Dataset → Compute dropdown → "Compute Batch" | Yes | `:314` `action="#{DatasetPage.canComputeAllFiles(false)}"` |
| 33 | Add Dataset to Compute Cart | `dataset.xhtml` | Access Dataset → Compute dropdown → "Add" | Yes | `:321` `action="#{DatasetPage.addItemtoCart(...)}"` |
| 34 | Remove Dataset from Compute Cart | `dataset.xhtml` | Access Dataset → Compute dropdown → "Remove" | Yes | `:329` `action="#{DatasetPage.removeCartItem(...)}"` |
| 35 | View Compute Cart List | `dataset.xhtml` | Access Dataset → Compute dropdown → "List" (opens popup) | Yes | `:335-338,1915` dialog `id="computeBatchListPopup"` |
| 36 | Clear Compute Cart | `dataset.xhtml` | Access Dataset → Compute dropdown → "Clear" | Yes | `:344` `action="#{DatasetPage.clearCart()}"` |
| 37 | Run Compute Batch | `dataset.xhtml` | Access Dataset → Compute dropdown → "Compute" outputLink | Yes | `:350` `value="#{DatasetPage.cartComputeUrl}"` |
| 38 | Submit Dataset for Review | `dataset.xhtml` | Edit/publish button group → "Submit for Review" | Yes | `:391` `rendered="#{showSubmitForReviewLink}"`, `action="#{DatasetPage.submitDataset}"` |
| 39 | Manage Dataset Permissions | `dataset.xhtml`, `permissions-manage.xhtml` | Edit Dataset menu → Permissions → "Dataset" link | Yes | `:455` `h:link outcome="permissions-manage"` |
| 40 | Manage File Permissions | `dataset.xhtml`, `permissions-manage-files.xhtml` | Edit Dataset menu → Permissions → "Files" link | Yes | `:461` `h:link outcome="permissions-manage-files"` |
| 41 | Create Private URL | `dataset.xhtml` | Edit Dataset menu → "Private URL" dialog → create button | Yes | `:475,1252` `action="#{DatasetPage.createPrivateUrl(false)}"` |
| 42 | Create Anonymized Private URL | `dataset.xhtml` | Private URL dialog → anonymized-access button | Yes | `:1294-1295` `action="#{DatasetPage.createPrivateUrl(true)}"` |
| 43 | Disable Private URL | `dataset.xhtml` | Private URL dialog → Disable → confirmation dialog | Yes | `:1355-1360` `id="disablePrivateUrlConfirmation"`, `action="#{DatasetPage.disablePrivateUrl()}"` |
| 44 | Copy Private URL to Clipboard | `dataset.xhtml` | Private URL dialog → copy icon next to URL | Yes | `:1269` `button class="btn-copy" data-clipboard-text` |
| 45 | Manage Thumbnails and Widgets | `dataset.xhtml`, `dataset-widgets.xhtml` | Edit Dataset menu → "Thumbnails + Widgets" link | Yes | `:481-482` `outputLink value="/dataset-widgets.xhtml?datasetId=..."` |
| 46 | Change Curation Status | `dataset.xhtml` | Publish/version bar → "Curation Status" dropdown | Yes | `:541` `action="#{DatasetPage.setCurationStatus(status)}"` |
| 47 | Remove Curation Status | `dataset.xhtml` | Curation Status dropdown → clear option | Yes | `:548` `action="#{DatasetPage.setCurationStatus(null)}"` |
| 48 | View Curation Status History | `dataset.xhtml` | Curation Status dropdown → "View Curation Status History" | Yes | `:556-559,2144` dialog `id="curationStatusHistoryDialog"` |
| 49 | View Dataset Citations Count | `dataset.xhtml` | Metrics widget → "N citations" link opens dialog | Yes | `:659,1103` dialog `id="citationsDialog"` |
| 50 | Rsync Data Access Popup | `dataset.xhtml`, `filesFragment.xhtml`, `file-data-access-fragment.xhtml` | Files tab → file row "Data Access" → rsync popup | Yes | `:1761` dialog `id="rsyncDataAccessPopup"` |
| 51 | Package Download Popup | `dataset.xhtml`, `package-download-popup-fragment.xhtml` | Access Dataset/file download → package download popup | Yes | `:1774` dialog `id="downloadPackagePopup"` |
| 52 | Compute Restricted-File Warning | `dataset.xhtml` | Compute dropdown → single-compute link with restricted files | Yes | `:1380-1381` dialog `id="computeInvalid"`, `dataset.compute.computeBatchRestricted` |
| 53 | Submit for Review Dialog Options | `dataset.xhtml` | Submit for Review dialog → disclaimer checkbox | Yes | `:1960-1972` `selectBooleanCheckbox id="submitForReviewDisclaimer"` |
| 189 | Return Dataset to Author | `dataset.xhtml` | Dataset page → Publish dropdown → "Return to Author" | Yes | `:399-405`, dialog `sendBackToContributor` (`:2114`) |
| 190 | Select Host Dataverse (Create mode) | `dataset.xhtml` | New Dataset form → "Host Dataverse" autocomplete | Yes | `:802-813` `p:autoComplete id="selectHostDataverse"` |
| 191 | Delete Selected Files | `dataset.xhtml` | Files tab → select files → "Delete" | Yes | `:1367` `p:dialog id="deleteSelectedFileConfirmation"` |
| 192 | Download Blocked by Restriction Dialog | `dataset.xhtml` | Files tab → select restricted files → Download | Yes | `:1128-1134` `p:dialog id="downloadInvalid"` with request-access link |
| 193 | Mixed Selection Download Continue | `dataset.xhtml` | Files tab → mixed selection → Download → "Continue" | Yes | `:1171-1191` `p:dialog id="downloadMixed"`, `startMultipleFileDownload()` |
| 194 | Mixed Selection Transfer Continue | `dataset.xhtml` | Files tab → mixed selection → Globus Transfer → "Continue" | Yes | `:1193-1210` `p:dialog id="globusTransferMixed"` |
| 195 | Publish Blocked - Parent Unpublished | `dataset.xhtml` | Dataset page → Publish when parent unpublished | Yes | `:2073-2090` `p:dialog id="mayNotRelease"` (`dataset.mayNotPublish.administrator`) |
| 196 | Publish Blocked - Two Generations Unpublished | `dataset.xhtml` | Dataset page → Publish when grandparent also unpublished | Yes | `:2091-2104` `p:dialog id="maynotPublishParent"` (`dataset.mayNotPublish.twoGenerations`) |
| 197 | Return to Author Reason Entry | `dataset.xhtml` | Return to Author dialog → reason textarea | Yes | `:2121-2124` `p:inputTextarea id="returnReason"` |

## Dataset Citation

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 198 | Cite Dataset in Multiple Styles | `dataset.xhtml` (includes `dataset-citation.xhtml`) | Dataset page → Cite button → "Style" dropdown | Yes | `:2195-2236` `select_CSL_Style` menu, `CSLUtil.getSupportedStyles` |

## Dataset Terms/License

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 199 | Enable File Access Requests Toggle | `dataset-license-terms.xhtml` | Edit Terms tab → "Request Access" checkbox | Yes | `:329` `termsOfUseAndAccess.fileAccessRequest` checkbox |

## Dataset Versions

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 54 | View Archival Copy Status | `dataset-versions.xhtml` | Versions tab → "Archival Copy" column | Yes | `:164-180` success/obsolete/pending/failure/notarchived states |
| 55 | Submit Version for Archiving | `dataset-versions.xhtml` | Versions tab → archived column → "Submit" link (superuser) | Yes | `:181-183` `archive-submit-link`, `action="DatasetPage.archiveVersion"` |
| 200 | View/Edit Version Note | `dataset-versions.xhtml` | Versions tab → draft row → "Version Note" link | Yes | `:137-145` `PF('editVersionNoteDialog').show()` |

## Dataset Metadata

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 201 | Select Metadata Language | `dataset.xhtml` | Dataset edit/create → Metadata Language field | Yes | `:213-230` `p:selectOneMenu id="dsMetadataLanguage"` |
| 202 | View/Edit Field Instructions (template) | `metadataFragment.xhtml` | Manage Templates → edit metadata field → inline instructions editor | Yes | `:261-262,343-344` `p:inplace id="instr"` bound to `TemplatePage.template.instructionsMap` |
| 203 | Add Replication Data Prefix | `metadataFragment.xhtml` | New Dataset → Title field → "Replication Data For" button | Yes | `:94-103` `input id="replicationDataButton"` prepends `dataset.replicationDataFor` |
| 204 | Use External Controlled-Vocabulary Lookup | `datasetFieldForEditFragment.xhtml` | Dataset metadata edit → CV-enabled field autocomplete | Yes | `:31-54` `data-cvoc-service-url`, `data-cvoc-protocol` attributes |

## Move Dataset

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 56 | Search/Select Dataset to Move | `dashboard-movedataset.xhtml` | Dashboard → Move Dataset → "Dataset" autocomplete | Yes | `:39-63` `p:autoComplete id="sourceDatasetMenu"` |
| 57 | Search/Select Destination Collection | `dashboard-movedataset.xhtml` | Move Dataset → "Move to Dataverse" autocomplete | Yes | `:82-104` `p:autoComplete id="destinationDataverseMenu"` |
| 58 | Move Dataset (Save) | `dashboard-movedataset.xhtml` | Move Dataset → "Save Changes" button | Yes | `:114-122` `commandButton id="move"` opens `moveDatasetConfirmation` |
| 59 | Confirm Move | `dashboard-movedataset.xhtml` | Move Dataset → confirmation dialog → "Yes" | Yes | `:133-136` `action="DashboardMoveDatasetPage.move()"` |
| 60 | Cancel Move Confirmation | `dashboard-movedataset.xhtml` | Move Dataset → confirmation dialog → "No" | Yes | `:137-139` `onclick="PF('moveDatasetConfirmation').hide()"` |
| 61 | Cancel Move Dataset Page | `dashboard-movedataset.xhtml` | Move Dataset page → "Cancel" link | Yes | `:123-127` `p:button outcome="dashboard" value="cancel"` |

## Contact Form

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 62 | Solve Math CAPTCHA | `contactFormFragment.xhtml` | Contact dialog (footer/header "Contact") → sum answer field | Yes | `:69-77` `op1 + op2 = messageSum`, `validateUserSum` |

## File Page

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 63 | Compute Access Denied Notice | `file.xhtml` | File page → Compute button (no download perm) → denial popup | Yes | `:710-713` `p:dialog id="computeAccessDenied"`, `file.compute.fileAccessDenied` |
| 205 | Export File Metadata | `file.xhtml` | File page → Metadata tab → "Export" dropdown | Yes | `:464-478` `dataset.exportBtn`, `FilePage.getExporters()` |

## File Data Access Tab

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 64 | View Rsync Access Instructions | `file-data-access-fragment.xhtml` | File page → Data Access tab → rsync command block | Yes | `:50-52` `rsyncDownloadcommand` via `repositoryStorageAbstractionLayerPage` |

## File Access & Download

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 65 | Globus Transfer | `file-download-button-fragment.xhtml`, `dataset.xhtml` | File/Dataset page → Download dropdown → "Globus Transfer" | Yes | `:65-85` `globus-btn`, `file.globus.transfer` |
| 66 | Download Package (Multi-file Bundle) | `file-download-button-fragment.xhtml`, `package-download-popup-fragment.xhtml` | Download dropdown → package link opens popup | Yes | `package-download-popup-fragment.xhtml:12-31` `packagePopupDownloadInfo` |
| 67 | Download Auxiliary File | `file-download-button-fragment.xhtml` | Download dropdown → Auxiliary Files submenu | Yes | `:273-295` `auxiliaryFileServiceBean.findAuxiliaryFiles` |
| 68 | Compute on File | `file-download-button-fragment.xhtml` | File page → "Compute" button/link | Yes | `:367-377` `btn-compute`, `FilePage.showComputeButton/computeUrl` |

## File Edit Options

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 69 | Uningest File | `file-edit-button-fragment.xhtml` | File page → Edit Files dropdown → "Uningest" | Yes | `:81-85` `action="FilePage.uningestFile()"`, `file.uningest` |
| 70 | Ingest File | `file-edit-button-fragment.xhtml` | Edit Files dropdown → "Ingest" | Yes | `:91-92` `actionListener="FilePage.ingestFile()"`, `file.ingest` |
| 71 | Set/Remove Retention Period | `file-edit-button-fragment.xhtml` | Edit Files dropdown → "Retention Period" popup | Yes | `:121-128` `fileRetentionPopup`, `file.retention` |
| 206 | Set/Remove Embargo | `file-edit-popup-fragment.xhtml` (included by `dataset.xhtml`) | Files tab → select files → "Embargo" action | Yes | `:96-125` `p:dialog id="fileEmbargoPopup"`, `bean.removeEmbargo` |

## File Provenance

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 72 | View Provenance Graph | `provenance/files_prov_tab.xhtml` | File page → Provenance tab → cytoscape graph area | Yes | `:20,146` `div id="fileForm:tabView:provenanceTab"`, `div id="cy"` |
| 73 | Toggle Ancestors/Successors | `provenance/files_prov_tab.xhtml` | Provenance tab → "Show Ancestors"/"Show Successors" checkboxes | Yes | `:160-163` `showAncestor()`/`showSuccessor()` |
| 74 | Upload Provenance JSON | `provenance-popups-fragment.xhtml` | File page → Edit → "Provenance" popup → file upload/drag-drop | Yes | `:46-58` `p:fileUpload id="provUpload" dragDropSupport="true"` |
| 75 | Preview Provenance JSON | `provenance-popups-fragment.xhtml` | Provenance popup → "Preview" button | Yes | `:68` `commandButton id="editProvenanceJsonPreview"` |
| 76 | Remove Provenance JSON | `provenance-popups-fragment.xhtml` | Provenance popup → "Remove" button | Yes | `:69` `commandButton id="editProvenanceJsonRemove"` |
| 77 | Select Provenance Entity | `provenance-popups-fragment.xhtml` | Provenance popup → entity dropdown | Yes | `:85-109` `p:autoComplete id="provJsonNameDropdown"` |
| 78 | Add Provenance Description | `provenance-popups-fragment.xhtml` | Provenance popup → "Description" textarea | Yes | `:125-131` `p:inputTextarea id="provenanceFreeform"` |
| 79 | Save Provenance Changes | `provenance-popups-fragment.xhtml` | Provenance confirm popup → "Save Changes" button | Yes | `:172-174` `commandButton id="confirmProvenancePopupSaveButton"` |

## Package Download Popup

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 80 | View Package Info | `package-download-popup-fragment.xhtml` | Dataset/file download → "Package" download popup | Yes | `packagePopupFragmentBean.fileMetadata`, `downloadPackagePopupCancelButton` |

## Edit Files (Upload)

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 81 | Download Rsync Upload Script | `editFilesFragment.xhtml` (in `editdatafiles.xhtml`) | Upload Files tab → rsync panel → "Download Rsync Script" | Yes | `rsyncDLEff` `actionListener="#{EditDatafilesPage.downloadRsyncScript()}"` |
| 82 | Upload Files via Dropbox | `editFilesFragment.xhtml` | Upload Files tab → "Upload with Dropbox" (feature-gated) | Yes | `dropBoxUserButton` `onclick="openDropboxChooser()"`, `rendered="#{settingsWrapper.isHasDropBoxKey()}"` |
| 83 | Upload Files via Globus | `editFilesFragment.xhtml` | Upload Files tab → "Upload with Globus" (feature-gated) | Yes | `globusBlock` opens `GlobusServiceBean.getGlobusAppUrlForDataset(dataset)` |
| 84 | Upload Files via Webloader | `editFilesFragment.xhtml` | Upload Files tab → "Upload with rsync+ssh/Webloader" (feature-gated) | Yes | `webloaderBlock` opens `EditDatafilesPage.getWebloaderUrlForDataset` |
| 85 | Set as Dataset Thumbnail | `editFilesFragment.xhtml` | Files table → file options dropdown → "Select as Dataset Thumbnail" | Yes | `fileSetThumbnailBtn` `actionListener="#{EditDatafilesPage.setFileMetadataSelectedForThumbnailPopup}"` |
| 86 | Advanced Ingest Options (Encoding) | `editFilesFragment.xhtml` | Files table → "Advanced Ingest Options" → SPSS-SAV encoding menu | Yes | `fileAdvancedOptions` dialog, `spssSavEncodingLanguage`, `setIngestEncoding` |
| 87 | Upload SPSS-POR Extra Labels File | `editFilesFragment.xhtml` | "Advanced Ingest Options" → SPSS-POR "Add Extra Labels" upload | Yes | `labelsFileUpload` `listener="#{EditDatafilesPage.handleLabelsFileUpload}"` |
| 88 | Resolve Duplicate/Type-Mismatch Upload | `editFilesFragment.xhtml` | Upload Files tab → duplicate/type-mismatch popup → "Delete" | Yes | `fileAlreadyExistsPopup`/`fileTypeDifferentPopup`, `action="#{EditDatafilesPage.deleteDuplicateFiles()}"` |

## Dataset Files Tab

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 89 | Toggle Table/Tree View | `filesFragment.xhtml` | Files tab → "Table"/"Tree" toggle (shown when folders exist) | Yes | `filesDisplayToggleBlock`, `DatasetPage.fileDisplayTable`/`fileDisplayTree` |
| 90 | Batch Globus Transfer | `filesFragment.xhtml` | Files tab → select files → Access/Download dropdown → "Transfer via Globus" | Yes | `DatasetPage.startGlobusTransfer(false,false)`, `file.globus.transfer` |
| 207 | Batch Request Access | `filesFragment.xhtml` | Files tab → select restricted files → "Request Access" | Yes | `:502-509` `fileAccessRequestMultiButtonRequired`, `validateFilesForRequestAccess()` |

## Manage Guestbooks

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 91 | Delete Guestbook | `manage-guestbooks.xhtml` | Manage Guestbooks page → guestbook row → trash icon | Yes | `commandLink action="#{manageGuestbooksPage.setSelectedGuestbook}"` opens `deleteConfirmation` |
| 92 | Confirm Delete Guestbook | `manage-guestbooks.xhtml` | Delete confirm dialog → "Continue" | Yes | `deleteGuestbookConfirm` dialog, `action="#{manageGuestbooksPage.deleteGuestbook()}"` |
| 93 | Cancel Delete Guestbook | `manage-guestbooks.xhtml` | Delete confirm dialog → "Cancel" | Yes | `onclick="PF('deleteConfirmation').hide()"` |

## Guestbook Preview Dialog

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 208 | Edit Guestbook from Preview | `guestbook-preview-popup-fragment.xhtml` (via `manage-guestbooks.xhtml`) | Manage Guestbooks → Preview dialog → Edit button | Yes | `manage-guestbooks.xhtml:165` `enableEdit=true`; fragment `:11-15` edit button |

## Guestbook Terms & Download Dialog

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 209 | Accept Terms and Start Globus Transfer | `guestbook-terms-popup-fragment.xhtml` (via `dataset.xhtml`) | Files tab → Globus Transfer → accept-terms dialog | Yes | `:283-290` `isGlobusTransfer`, `writeGuestbookAndStartDownload(...,true)` |
| 210 | Accept Terms and Preview File | `guestbook-terms-popup-fragment.xhtml` (via `file.xhtml`) | File Preview tab → accept terms | Yes | `:292-298` `popupContext=='previewTab'`, `FilePage.showPreview` |
| 211 | Accept Terms and Launch External Tool | `guestbook-terms-popup-fragment.xhtml` | File/Dataset page → "Explore" external tool → accept terms | Yes | `:301-305` `fileFormat=='externalTool'`, `writeGuestbookAndLaunchExploreTool` |
| 212 | Accept Terms and Download Package | `guestbook-terms-popup-fragment.xhtml` | Files tab → download package → accept terms | Yes | `:307-311` `fileFormat=='package'`, `writeGuestbookAndLaunchPackagePopup` |

## Guestbook Responses

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 213 | Sort Responses Table | `guestbook-responses.xhtml` | Manage Guestbooks → view responses → click column header | Yes | `:73-85` `p:column sortBy="#{response[0..4]}"` |

## Manage Templates / Template (Create/Edit)

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 94 | Make Default Template | `manage-templates.xhtml` | Manage Templates → template row → "Make Default" | Yes | `actionListener="#{manageTemplatesPage.makeDefault(template)}"` |
| 95 | Unset Default Template | `manage-templates.xhtml` | Template row → "Default" (eye icon) to unset | Yes | `actionListener="#{manageTemplatesPage.unselectDefault(template)}"` |
| 214 | Save Template Changes | `template.xhtml` | Manage Templates → edit template → "Save Changes" | Yes | `:117-125` `TemplatePage.save('Terms')` / `save('')` |

## Login Page

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 96 | Contact Support | `loginpage.xhtml` | Institutional login support blurb → support-team link opens contact dialog | Yes | `p:commandLink oncomplete="PF('contactForm').show()"` |
| 215 | Forgot Password | `loginpage.xhtml` | Login page → "Forgot your password?" link | Yes | `:101-103` link to `passwordreset.xhtml` |
| 216 | Log In via Your Institution | `loginpage.xhtml` | Login page → Shibboleth tab → WayFinder/institution search | Yes | `:109-173` remote provider (`shib`) section |
| 217 | Log In via ORCID or Other OAuth Provider | `loginpage.xhtml` | Login page → ORCID/Google/GitHub button | Yes | `:179-215` `LoginPage.authProvider.OAuthProvider` button |
| 218 | Switch Login Method | `loginpage.xhtml` | Login page → "other providers" list of auth methods | Yes | `:217-225` `setAuthProviderById(provider.id)` |
| 219 | Sign Up | `loginpage.xhtml` | Login page → sign-up blurb/link | Yes | `:236-242` `signUpLink` div |

## Confirm Email

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 97 | Confirm Email Address | `confirmemail.xhtml` | Emailed link → `/confirmemail.xhtml` verifies token | Yes | `f:viewAction action="#{ConfirmEmailPage.init}"`, `viewParam token` |
| 98 | Go to Account Page | `confirmemail.xhtml` | Confirm Email page (invalid token) → "Go to Account Page" | Yes | `rendered="#{ConfirmEmailPage.invalidToken}"` → `/dataverseuser.xhtml?selectTab=accountInfo` |

## Institutional Login (Shibboleth)

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 99 | Create New Account | `shib.xhtml` | Institutional login → "Create Account" tab → terms → "Create Account" | Yes | `action="#{Shib.confirmAndCreateAccount()}"`, `rendered="#{Shib.offerToCreateNewAccount}"` |
| 100 | Cancel Account Creation | `shib.xhtml` | "Create Account" form → "Cancel" link (returns to `/`) | Yes | `<a href="/" class="btn btn-default">Cancel</a>` |
| 101 | Convert Existing Account | `shib.xhtml` | "Convert Account" tab → enter password → "Convert Account" | Yes | `action="#{Shib.confirmAndConvertAccount()}"`, `rendered="#{Shib.offerToConvertExistingAccount}"` |
| 102 | Forgot Password | `shib.xhtml` | "Convert Account" form → "Forgot your password?" link | Yes | `<a href="passwordreset.xhtml">` |

## Convert Account (OAuth)

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 103 | Convert Existing Account | `oauth2/convert.xhtml` | OAuth first-login flow → "Convert Account" tab → Convert button | Yes | `action="#{OAuth2FirstLoginPage.convertExistingAccount}"` |
| 104 | Cancel | `oauth2/convert.xhtml` | Convert-account form → "Cancel" (returns to first-login page) | Yes | `action="/oauth2/firstLogin.xhtml?faces-redirect=true"` |

## ORCID Confirmation

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 105 | Contact Support | `oauth2/orcidConfirm.xhtml` | ORCID callback error page → support-team link opens contact dialog | Yes | `oncomplete="PF('contactForm').show()"` |

## Account Information

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 106 | Edit Account Information | `dataverseuser.xhtml` | My Account → Account Information → "Edit Account" dropdown → "Account Information" | Yes | `commandLink id="editAccount" actionListener="#{DataverseUserPage.edit}"` |
| 107 | Save Account Changes | `dataverseuser.xhtml` | Account Information tab (edit mode) → "Save Changes" | Yes | `:876` `action="#{DataverseUserPage.save}"` |
| 108 | Change Password | `dataverseuser.xhtml` | Account Information → "Edit Account" dropdown → "Password" | Yes | `commandLink id="changePassword" actionListener="#{DataverseUserPage.changePassword}"` |
| 109 | Save New Password | `dataverseuser.xhtml` | Password edit mode → current/new password fields → "Save Changes" | Yes | `p:password id="inputPassword"/"currentPassword"`, `action="#{DataverseUserPage.save}"` |
| 110 | Cancel Edit | `dataverseuser.xhtml` | Account edit mode → "Cancel" button | Yes | `commandButton id="cancel" action="#{DataverseUserPage.cancel}"` |
| 111 | Remove ORCID iD | `dataverseuser.xhtml` | "Edit Account" dropdown → "Remove ORCID iD" | Yes | `commandLink id="removeOrcid" actionListener="#{DataverseUserPage.removeOrcid}"` |
| 112 | Link/Authenticate ORCID iD | `dataverseuser.xhtml` | Account Information → ORCID row → "Authenticate" | Yes | `action="#{DataverseUserPage.startOrcidAuthentication()}"` |
| 113 | Verify Email Address | `dataverseuser.xhtml` | Account Information → Email row → "Verify Email" (unverified) | Yes | `commandLink id="verifyEmailButton" action="#{DataverseUserPage.sendConfirmEmail()}"` |
| 114 | Contact Support | `dataverseuser.xhtml` | Shib/OAuth migration help text → support-team link | Yes | `:546,559` `oncomplete="PF('contactForm').show()"` |
| 224 | Create Account | `dataverseuser.xhtml` | Sign Up form (username/affiliation/position/etc.) | Yes | `:745-853` CREATE-mode fields (`userName`, `affiliation`, `position`) |

## Notifications

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 115 | Manage Muted Email Notifications | `dataverseuser.xhtml` | Notifications tab → "Mute Options" → "Muted Emails" checkboxes → Save | Yes | `mutedEmails` selectItems, `DataverseUserPage.notificationTypeList` |
| 116 | Manage Muted In-App Notifications | `dataverseuser.xhtml` | Notifications tab → "Mute Options" → "Muted Notifications" checkboxes → Save | Yes | `mutedNotifications` `p:selectManyCheckbox value="#{DataverseUserPage.toReceiveNotifications}"` |

## My Data

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 117 | Filter by Metadata Validity | `mydata_page.xhtml`, `mydata_fragment.xhtml` | My Data page → left sidebar "Metadata Validity" filter checkboxes | Yes | `:83-98` `showValidityFilter()`, `validityInfoForCheckboxes` |
| 225 | Paginate Results | `mydata_page.xhtml`, `mydata_fragment.xhtml` | My Data page → pagination controls below results | Yes | `:108-133` `div id="div-pagination"`, `mydata.viewnext` |

## Manage Permissions

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 118 | Configure Default Access Settings | `permissions-manage.xhtml`, `permissions-configure.xhtml` | Manage Permissions → "Configure" gear button → access dialog | Yes | `:44-48` `commandLink id="configureButton"` opens `accessDialog` |
| 119 | Assign Role | `permissions-manage.xhtml`, `roles-assign.xhtml` | Manage Permissions → Users/Groups panel → "Assign Role" | Yes | `userGroupDialog`, `managePermissionsPage.assignRole` |
| 120 | Remove Role Assignment | `permissions-manage.xhtml` | Assigned roles table → remove (×) link + confirmation | Yes | `:135-141` `removeBtn`, `accessRemoveConfirm` dialog `:272-285` |
| 121 | Create Custom Role | `permissions-manage.xhtml`, `roles-edit.xhtml` | Roles panel → "+" Add Role button | Yes | `:164-171` `rolesAdd`, `createNewRole` |
| 122 | Duplicate Role | `permissions-manage.xhtml`, `roles-edit.xhtml` | Roles panel → role row → duplicate (copy) icon | Yes | `:185-190` `cloneRole(role.id)` |
| 123 | Edit Role | `permissions-manage.xhtml`, `roles-edit.xhtml` | Roles panel → role row → pencil (edit) icon | Yes | `:179-184` `editRole(role.id)` |
| 124 | Save Role | `roles-edit.xhtml` | Role editor dialog → "Save Changes" | Yes | `:75-82` `commandButton saveChanges`, `updateRole` |
| 125 | Download Role Assignment History | `permissions-manage.xhtml` | Role Assignment History panel → download CSV link | Yes | `:212-216` `signedUrlForRAHistoryCsv`, `downloadRAHistoryCSV` |

## Manage File Permissions

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 126 | Grant File Access | `permissions-manage-files.xhtml` | Restricted file row → "Grant Access" (+) button | Yes | `:215-218` `assignBtn`, `initAssignDialogByFile` |
| 127 | Grant All File Access Requests | `permissions-manage-files.xhtml` | Access requests table → "Grant" button per user | Yes | `:95-103` `grantAccessToAllRequests` |
| 128 | Grant Selected File Access Requests | `permissions-manage-files.xhtml` | Assign dialog → select files → "Grant" | Yes | `:407-412` `grantAccessToRequests` |
| 129 | Reject All File Access Requests | `permissions-manage-files.xhtml` | Access requests table → "Reject" button per user | Yes | `:104-112` `rejectAccessToAllRequests` |
| 130 | Reject Selected File Access Requests | `permissions-manage-files.xhtml` | Assign dialog → select files → "Reject" | Yes | `:413-418` `rejectAccessToRequests` |
| 131 | Revoke File Access | `permissions-manage-files.xhtml` | View/remove dialog → select rows → "Remove" + confirm | Yes | `:311-315,425-439` `removeRoleAssignments` |
| 132 | Toggle Show Deleted Files | `permissions-manage-files.xhtml` | "Include deleted files" checkbox | Yes | `:52,171` `showDeleted`/`showDeletedCheckboxChange` |
| 133 | Toggle Show Access Request History | `permissions-manage-files.xhtml` | "Show History" checkbox | Yes | `:55` `showHistory`/`showHistoryCheckboxChange` |
| 134 | Download File Permissions History | `permissions-manage-files.xhtml` | Role Assignment History panel → download CSV link | Yes | `:236-240` `signedUrlForRAHistoryCsv` |

## Manage Groups

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 135 | Create Explicit Group | `manage-groups.xhtml`, `explicitGroup-new-dialog.xhtml` | Manage Groups → "+ Create Group" | Yes | `:25-29` `createGroup`, `initExplicitGroupDialog` |
| 136 | Edit Group Membership | `manage-groups.xhtml` | Group row → edit (pencil) icon → viewGroup dialog → add members → Save | Yes | `:71-77,117-137,170-174` `viewSelectedGroup`, `saveExplicitGroup` |
| 137 | Remove Group Member | `manage-groups.xhtml` | viewGroup dialog → member row → trash icon | Yes | `:157-166` `removeMemberFromSelectedGroup` |
| 138 | Delete Group | `manage-groups.xhtml` | Group row → trash icon + confirm dialog | Yes | `:78-84,90-98` `clickDeleteGroup`/`deleteGroup` |

## Role Permission Helper

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 139 | View Role/Permission Matrix | `role_permission_helper.xhtml` | Direct URL `role_permission_helper.xhtml` — read-only matrix table | **Partial** | `:36-49` `rolesByDvObjectTable` exists; no in-app menu link to this page was found in any xhtml |

## Private URL

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 140 | Create Private URL | `dataset.xhtml` | Edit dropdown → "Private URL" dialog → "Create URL" | Yes | `:475-476,1251-1254` `createPrivateUrl(false)` |
| 141 | Copy Private URL Link | `dataset.xhtml` | Private URL dialog → generated link → "Copy" clipboard button | Yes | `:1269` `btn-copy data-clipboard-text` |
| 142 | Disable Private URL | `dataset.xhtml` | Private URL dialog → "Disable" + confirm | Yes | `:1272,1359-1360` `disablePrivateUrl()` |
| 226 | Access Dataset via Private URL | `privateurl.xhtml` | Visiting a Private URL link | Yes | `:17-19` `f:viewParam name="token"`, `PrivateUrlPage.init()` |

## Preview URL

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 143 | Create Anonymized Access Preview URL | `dataset.xhtml` | Private URL dialog → "Anonymized Access" section → "Create URL" | Yes | `:1277-1299` `createPrivateUrl(true)` |
| 144 | Copy Preview URL Link | `dataset.xhtml` | Anonymized section → generated link → "Copy" | Yes | `:1309-1316` `btn-copy data-clipboard-text` |
| 145 | Disable Preview URL | `dataset.xhtml` | Anonymized section → "Disable" + confirm | Yes | `:1319,1359` `disablePrivateUrl()` |
| 227 | Access Dataset via Preview URL | `previewurl.xhtml` | Visiting a Preview URL link | Yes | `:17-19` `f:viewParam name="token"`, `PrivateUrlPage.init()` |

## Harvesting Clients

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 146 | Create Harvesting Client (Step 1 - Info) | `harvestclients.xhtml` | Dashboard → Harvesting Clients → "+ Add Client" → wizard Step 1 | Yes | `:187-329` `createStepOne`, `validateInitialSettings` |
| 147 | Create Harvesting Client (Step 2 - Format) | `harvestclients.xhtml` | Wizard Step 2 (OAI set + metadata format) | Yes | `:331-416` `createStepTwo`, `oaiSetsSelectItems` |
| 148 | Create Harvesting Client (Step 3 - Schedule) | `harvestclients.xhtml` | Wizard Step 3 (schedule) | Yes | `:418-509` `createStepThree`, `harvestingScheduleRadio` |
| 149 | Create Harvesting Client (Step 4 - Display) | `harvestclients.xhtml` | Wizard Step 4 (display style) → "Create" | Yes | `:511-595` `createStepFour`, `createClient` |
| 150 | Run Harvest Now | `harvestclients.xhtml` | Harvesting Clients table → row → play icon | Yes | `:118-124` `runHarvest(harvestClient)` |
| 151 | Edit Harvesting Client | `harvestclients.xhtml` | Clients table → row → pencil icon reopens wizard | Yes | `:125-132` `editClient(harvestClient)` |
| 152 | Save Harvesting Client | `harvestclients.xhtml` | Wizard Step 4 (edit mode) → "Save" | Yes | `:582-589` `saveClient` |
| 153 | Delete Harvesting Client | `harvestclients.xhtml` | Clients table → row → trash icon + warning dialog | Yes | `:133-140,157-176` `setClientForDelete`/`deleteClient` |
| 154 | Cancel Harvesting Client Dialog | `harvestclients.xhtml` | Wizard dialog → "Cancel" link (any step) | Yes | `:322-326` `PF('newHarvestingClientForm').hide()` |
| 155 | Navigate Wizard Steps | `harvestclients.xhtml` | Wizard dialog → "Previous"/"Next" links | Yes | `backToStepOne/Two/Three`, `goToStepThree/Four` |

## Harvesting Sets

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 156 | Toggle Harvesting Server On/Off | `harvestsets.xhtml` | Dashboard → Harvesting Server → "Service" dropdown | Yes | `:29-37` `oaiServerStatusRadio`, `toggleHarvestingServerStatus` |
| 157 | Create OAI Set (Enter Query) | `harvestsets.xhtml` | "+ Add Set" → new set dialog query step | Yes | `:57-63,203-231` `initNewSet`, `validateSetQuery` |
| 158 | Create OAI Set (Name & Describe) | `harvestsets.xhtml` | New set dialog step 2 (setspec/description) → "Create" | Yes | `:261-310` `addSetStepTwo`, `createSet` |
| 159 | Run Set Export Now | `harvestsets.xhtml` | Sets table → row → play icon | Yes | `:150-156` `startSetExport(oaiSet)` |
| 160 | Edit OAI Set | `harvestsets.xhtml` | Sets table → row → pencil icon reopens dialog | Yes | `:157-164` `editSet(oaiSet)` |
| 161 | Save OAI Set | `harvestsets.xhtml` | New set dialog (edit mode) → "Save" | Yes | `:311-316` `saveSet` |
| 162 | Delete OAI Set | `harvestsets.xhtml` | Sets table → row → trash icon (disabled for default) + warning | Yes | `:165-172,178-190` `setSelectedSet`/`deleteSet` |
| 163 | Cancel OAI Set Dialog | `harvestsets.xhtml` | New set dialog → "Cancel" link | Yes | `:252-255,317-319` `PF('newOAISetForm').hide()` |
| 164 | Navigate Set Creation Steps | `harvestsets.xhtml` | New set dialog step 2 → "Previous" link back to query step | Yes | `:296-302` `backToQuery()` |

## Dashboard

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 165 | View Dashboard Metrics | `dashboard.xhtml` | Dashboard → summary cards (top of page) | Yes | Cards show `DashboardUsersPage.getUserCount/getSuperUserCount`, harvest client/OAI set/dataset/dataverse counts |
| 166 | Go to Manage Harvesting Clients | `dashboard.xhtml` | Dashboard → Harvesting Clients card → "Manage" | Yes | `:55` link to `harvestclients.xhtml` |
| 167 | Go to Manage Harvesting Server | `dashboard.xhtml` | Dashboard → Harvesting Server card → "Manage" | Yes | `:84` link to `harvestsets.xhtml` |
| 168 | Go to Manage Users | `dashboard.xhtml` | Dashboard → Users card → "Manage Users" | Yes | `:122` link to `dashboard-users.xhtml` |
| 169 | Go to Move Dataset Tool | `dashboard.xhtml` | Dashboard → Move Data card → "Manage" (dataset) | Yes | `:145` link to `dashboard-movedataset.xhtml` |
| 170 | Go to Move Dataverse Tool | `dashboard.xhtml` | Dashboard → Move Data card → "Manage" (dataverse) | Yes | `:150` link to `dashboard-movedataverse.xhtml` |

## Manage Users

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 171 | Search Users | `dashboard-users.xhtml` | Manage Users page → search box + find icon | Yes | `:32-39` search input, `DashboardUsersPage.runUserSearch()` |
| 172 | Sort User List | `dashboard-users.xhtml` | Manage Users page → "Sort" dropdown | Yes | `:48-58` `runUserSearchWithSort(sortFieldEntry.key)` |
| 173 | Page Through User List | `dashboard-users.xhtml`, `dashboard-users-pager.xhtml` | Pager controls above user table | Yes | `:64-66` `ui:include dashboard-users-pager.xhtml` |
| 174 | Toggle Superuser Status | `dashboard-users.xhtml` | User table → superuser checkbox column | Yes | `:108-113` `superUserCheckbox` + confirmation dialog |
| 175 | Cancel Superuser Status Change | `dashboard-users.xhtml` | Superuser confirmation dialog → "No" | Yes | `:125` `cancelSuperuserStatusChange()` |
| 176 | Remove All User Roles | `dashboard-users.xhtml` | User table → "Remove all" roles button + confirm | Yes | `:91-100,128-135` `removeUserRoles()` |

## Superuser

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 177 | Index All | `superuser.xhtml` | `/superuser.xhtml` → "Index All" button | Yes | `:25-27` `action="SuperUserPage.startIndexAll()"` |
| 178 | Check Status of Index All | `superuser.xhtml` | Superuser page → "Check Status of Index All" | Yes | `:28-32` `SuperUserPage.updateIndexAllStatus()` |

## Error Pages

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 179 | 404 Static Fallback Page | `404static.xhtml` | Not user-navigable; served as static error fallback | Yes | Standalone page, `error.404.message`, no template |
| 231 | 403 Forbidden Page | `403.xhtml` | Navigate to a permission-denied resource | Yes | `:20-30` `error.403.message`, contact-support commandLink |
| 232 | 500 Internal Server Error Page | `500.xhtml` | Server error triggers this page | Yes | `:18` `error.500.message` |

## Embeddable Widgets

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 180 | Dataset Citation iFrame | `iframe.xhtml` | Not menu-accessible; loaded via `/iframe.xhtml?persistentId=...` in an external embed | Yes | Includes `dataset-citation.xhtml`; `top!=self` redirects to `dataset.xhtml` |

## DataTags Test Tool

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 181 | Submit Dataset Name for DataTags Interview | `datatags-api-test.xhtml` | Dev-only page → "Tag your dataset" button | Yes | `commandButton "Tag your dataset" action="dataTagsAPITestingBean.requestInterview"` |
| 182 | DataTags Deposit Complete (Test Display) | `datatags-api-test-deposit-complete.xhtml` | Dev-only page shown after DataTags interview redirect | Yes | Outputs `dataTagsAPITestingBean.datasetName` and `.tags` |

## Search Results

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 228 | Copy File Checksum/UNF Value | `search-include-fragment.xhtml` | Search results → file card → checksum/UNF copy icon | Yes | `:688-711` `glyphicon-copy`, `data-clipboard-text="#{result.fileChecksumValue}"` |
| 229 | View Technical Details of Search Error | `search-include-fragment.xhtml` | Search results → Solr error banner → "[+] technical details" | Yes | `:313-318` `[+] dataverse.results.empty.link.technicalDetails` |
| 230 | Contact Support (No Results Guidance) | `search-include-fragment.xhtml` | Zero-results banner (search/browse) | **Partial** | `:296-335` shows guidance/sign-up links via bundle keys, but no explicit "Contact Support" action tied specifically to the no-results case |

## OAuth Login Callback

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 223 | Contact Support | `oauth2/callback.xhtml` | OAuth error page → "contact ... support" link | Yes | `:36-45` `sendFeedbackDialog.initUserInput`, `contactForm` |

## Password Reset

| # | Functionality | JSF Page(s) | How to locate in the UI | Status | Evidence |
|---|---|---|---|---|---|
| 220 | Request Password Reset Email | `passwordreset.xhtml` | Password Reset page → enter email → submit | Yes | `:45-58` `PasswordResetPage.sendPasswordResetLink()` |
| 221 | Cancel | `passwordreset.xhtml` | Password Reset page → "Cancel" button | Yes | `:59` `p:button outcome="/loginpage.xhtml"` |
| 222 | Set New Password | `passwordreset.xhtml` | Reset email link → new/retype password form | Yes | `:111-147` `PasswordResetPage.resetPassword()` |

---

*Generated by cross-referencing [`DV - Missing items.txt`](./DV%20-%20Missing%20items.txt) against `src/main/webapp/**/*.xhtml` and corresponding backing beans in `src/main/java`.*
