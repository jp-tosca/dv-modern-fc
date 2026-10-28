# GitHub Item Classifier

`classify_github_items.py` is a standalone Python script that reads a table of links to GitHub issues, pull requests, and discussions, fetches each item's title, body, and labels from GitHub, and classifies each item by the kind of user or task it concerns.

Every item is assigned to exactly one of three categories:

1. **Data Depositors, Seekers, and Downloaders**
2. **Data Curators and Installation Administrators**
3. **Other**

The output is a table with three columns: `Title`, `Link`, and `Classification`.

---

## Table of contents

- [Quick start](#quick-start)
- [Input](#input)
- [Output](#output)
- [Command-line options](#command-line-options)
- [Classification rubric](#classification-rubric)
- [How an item is classified](#how-an-item-is-classified)
- [Classification modes](#classification-modes)
- [Customizing the classifier](#customizing-the-classifier)
- [Error handling and rate limits](#error-handling-and-rate-limits)
- [Limitations](#limitations)

---

## Quick start

```bash
pip install requests          # required
pip install openpyxl          # only needed for .xlsx input/output

export GITHUB_TOKEN=ghp_xxx   # recommended; required for discussions

python classify_github_items.py items.csv -o items_classified.csv
```

Requires Python 3.8+.

### Environment variables

| Variable | Required? | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | Recommended | Raises the GitHub API rate limit from 60 to 5,000 requests per hour. **Required** to read discussions, which are only available through GitHub's GraphQL API. A token with read access to the repositories is sufficient (add the `repo` scope for private repositories). |
| `ANTHROPIC_API_KEY` | Only with `--use-claude` | Used to call the Anthropic API for LLM-based classification. |

---

## Input

A CSV, TSV, or XLSX file with a header row and at least one column containing GitHub links. Other columns are allowed and ignored.

| File extension | Format |
|---|---|
| `.csv` (or anything else) | Comma-separated |
| `.tsv`, `.tab` | Tab-separated |
| `.xlsx`, `.xlsm` | Excel (first sheet; requires `openpyxl`) |

Supported link formats:

```
https://github.com/<owner>/<repo>/issues/<number>
https://github.com/<owner>/<repo>/pull/<number>
https://github.com/<owner>/<repo>/discussions/<number>
```

The link column is auto-detected as the first column that contains at least one such link. If detection fails or you want a different column, pass `--link-column "Column Name"`.

Example input:

```csv
URL,Owner
https://github.com/IQSS/dataverse/issues/1234,Alice
https://github.com/IQSS/dataverse/issues/5678,Bob
```

## Output

A file with the same format as the input, by default named `<input>_classified.<ext>` (override with `-o`). Columns:

| Column | Description |
|---|---|
| `Title` | The GitHub item's title |
| `Link` | The item's URL, as given in the input |
| `Classification` | One of the three categories, or `Unclassified (could not fetch item)` |

Example output:

```csv
Title,Link,Classification
Guestbook not shown when downloading files,https://github.com/IQSS/dataverse/issues/1234,"Data Depositors, Seekers, and Downloaders"
Add custom metadata block loader,https://github.com/IQSS/dataverse/issues/5678,Data Curators and Installation Administrators
```

Progress is logged to stderr, one line per item, including the assigned category and any labels or intended-user statement that were detected.

---

## Command-line options

```
python classify_github_items.py INPUT [-o OUTPUT] [--link-column NAME]
                                [--use-claude] [--model MODEL] [--delay SECONDS]
```

| Option | Default | Description |
|---|---|---|
| `INPUT` | (required) | Input CSV/TSV/XLSX file |
| `-o`, `--output` | `<input>_classified.<ext>` | Output file; format follows the extension |
| `--link-column` | auto-detect | Name of the column containing GitHub links (case-insensitive) |
| `--use-claude` | off | Classify with the Anthropic API instead of the built-in keyword rules |
| `--model` | `claude-sonnet-5-5` | Model used with `--use-claude` |
| `--delay` | `0.2` | Seconds to pause between GitHub requests |

---

## Classification rubric

The rubric describes who a GitHub item is for and what task it concerns.

### 1. Data Depositors, Seekers, and Downloaders

Items about **common end-user tasks**, including:

- Creating an account
- Searching for data
- Requesting access to datasets
- Downloading data
- Depositing datasets
- Editing datasets
- Adding datasets' terms of use
- Creating guestbooks

*Typical audience:* researchers, students, depositors, data seekers, data downloaders, anonymous or logged-in visitors.

*Typical labels:* `Feature: Account & User Info`, `Feature: Search/Browse`, `Feature: File Upload & Handling`.

### 2. Data Curators and Installation Administrators

Items about **common data curation tasks**, including:

- Reviewing datasets
- Publishing datasets
- Adding new collection members
- Changing collection user permissions
- Changing curation status
- Adding custom metadata blocks

Also included in this category are installation-level content and user administration tasks closely related to the above, such as managing user accounts across the installation, using superuser tools or dashboards, and loading metadata blocks.

*Typical audience:* curators, collection or repository administrators, librarians, data stewards, reviewers, superusers, installation administrators.

*Typical labels:* labels about curation, review, publishing, permissions, roles, or metadata blocks.

### 3. Other

Items about **other tasks, including system configuration and administration tasks**, such as:

- Server, database, and application configuration (JVM options, database settings)
- Installation, deployment, and upgrades (Docker, Kubernetes, Payara, Solr, PostgreSQL)
- Software development work (builds, CI, tests, refactoring, dependency updates)
- APIs, harvesting, and integrations (REST/native API, SWORD, OAI-PMH)
- Storage, DNS, DOI provider, and mail server configuration
- Documentation and release notes

*Typical audience:* developers, integrators, DevOps staff, operators, system maintainers.

Items that match none of the above signals strongly enough also fall into this category.

### Boundary guidance

The rubric places "system configuration and administration tasks" under **Other** but also includes installation administrators in category 2. The script resolves this as follows:

| Task | Category |
|---|---|
| Managing users, roles, or content *within* the repository platform (adding collection members, loading a custom metadata block, merging or deactivating accounts, superuser tools) | Data Curators and Installation Administrators |
| Configuring or operating the *software and infrastructure* itself (JVM settings, deployment, Solr, storage drivers, mail server, CI) | Other |

If your team draws this boundary differently, adjust the rules described under [Customizing the classifier](#customizing-the-classifier).

---

## How an item is classified

Each item receives a score for each of the three categories from four sources of evidence. The highest-scoring category wins.

### 1. Title and body keyword rules

Regular-expression rules (case-insensitive) map phrases to categories, each with a weight from 1 to 4. For example, "guestbook" is a strong end-user signal, "custom metadata block" is a strong curator/administrator signal, and "JVM options" is a signal for Other.

- Every occurrence in the body adds the rule's weight.
- Matches in the **title** count **double** (`TITLE_MULTIPLIER = 2`).
- Fenced code blocks, inline code, URLs, and HTML comments are stripped first, so pasted logs and stack traces don't skew results.

Representative signals:

| Category | Example signals |
|---|---|
| Depositors, Seekers, Downloaders | creating an account, sign up/log in, searching or browsing data, requesting access, restricted files, downloading, depositing or uploading datasets, creating a dataset, editing datasets/metadata/files, terms of use or license, guestbooks, "end user", "researcher", "depositor" |
| Curators and Installation Administrators | reviewing or publishing datasets, submit for review, return to author, adding or removing collection members, collection roles and permissions, curation status/labels/workflow, "curator", custom metadata blocks, loading metadata block TSVs, superuser, admin dashboard, deactivating or merging user accounts, installation-wide changes, "installation administrator", "sysadmin" |
| Other | configuration, JVM options, database settings, install/deploy/upgrade, Docker, Kubernetes, Payara, Solr, PostgreSQL, build/Maven/CI, unit and integration tests, refactoring, dependencies, API endpoints/tokens, SWORD, OAI-PMH, harvesting, documentation, release notes, S3/storage drivers, DNS, DOI providers, SMTP |

### 2. Labels

Each GitHub label is checked against a label-specific pattern table (`LABEL_RULES`). A match adds **+4** to the matching category, once per label. Examples:

| Label | Effect |
|---|---|
| `Feature: Account & User Info` | + Depositors, Seekers, Downloaders |
| `Feature: Search/Browse` | + Depositors, Seekers, Downloaders |
| `Feature: File Upload & Handling` | + Depositors, Seekers, Downloaders |
| `Feature: Permissions & Roles` | + Curators and Installation Administrators |
| `Feature: Curation` | + Curators and Installation Administrators |
| `Feature: Installation`, `Feature: API` | + Other |

Labels that explicitly **name a user type** (prefixes such as `User:`, `User Role:`, `Role:`, `Persona:`, `Audience:`, `Intended User:`, `Target User:`) are interpreted using the intended-user mapping below and add **+6** to each matching category.

### 3. Explicit statement of the intended user

If the body states who the item is for, that statement is extracted and given heavy weight (**+10** to each matching category).

The script recognizes questions and labels such as:

- "What kind of user is the feature intended for?"
- "Who is this feature for?" / "Who will use this?"
- "Intended user:", "Target audience:", "User type / persona"

in any of these layouts:

- A Markdown heading followed by the answer (the layout produced by GitHub issue forms)
- A bold label followed by the answer
- An inline `Label: answer` line

Handling details:

- For checkbox answers, only **checked** options are used.
- Empty or placeholder answers (`_No response_`, `N/A`, `TBD`, `none`, unchecked boxes) are ignored.
- An ordinary sentence that merely mentions "users" is not treated as an intended-user statement.
- If the answer names several user types (e.g. "researchers and curators"), every matching category gets the bonus, and the remaining evidence decides.

How stated users map to categories:

| Stated user | Category |
|---|---|
| depositor, data seeker/downloader/consumer, end user, researcher, scientist, student, author, public, anonymous or logged-in user, guest | Data Depositors, Seekers, and Downloaders |
| curator, installation administrator, collection/dataverse/repository admin or manager, administrator, superuser, sysadmin, librarian, data steward, reviewer, moderator | Data Curators and Installation Administrators |
| developer, integrator, DevOps, operator, maintainer, programmer, API client, third-party developer/tool, deployer | Other |

### 4. Decision rule

1. Sum the scores from the three sources above for each category.
2. If the highest score is below the minimum threshold (`MIN_SCORE = 3`), the item is classified as **Other**.
3. Otherwise the highest-scoring category wins. Ties are broken in the order: Depositors/Seekers/Downloaders, then Curators/Administrators, then Other.

Because the explicit intended-user bonus (+10) is large relative to typical keyword weights (1–4), a clear statement from the item's author will usually decide the outcome, but a body that overwhelmingly points the other way can still outweigh it.

---

## Classification modes

### Keyword mode (default)

Deterministic, offline (apart from fetching items from GitHub), free, and repeatable. Best when items follow common phrasing and your labels are informative.

### Claude mode (`--use-claude`)

Sends the rubric, the item's title, labels, intended-user statement (if found), and the first 8,000 characters of the body to the Anthropic API, and asks the model to choose one category. The prompt tells the model to treat an explicit intended-user statement as strong evidence and to interpret labels as described above. This handles ambiguous or mixed-topic items better, at the cost of API usage and slightly less predictable results. The response is validated; anything that doesn't match a known category falls back to **Other**.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python classify_github_items.py items.csv --use-claude
```

---

## Customizing the classifier

All tunable settings are near the top of the script:

| Setting | Purpose |
|---|---|
| `RULES` | Title/body keyword rules: `(regex, weight)` per category |
| `LABEL_RULES` | Label patterns per category; adapt to your repository's label taxonomy |
| `USER_RULES` | Words that map a stated intended user to a category |
| `USER_LABEL_RE` | Which label prefixes are treated as user-type labels |
| `QUESTION_RE` | Phrases recognized as an "intended user" question or label |
| `TITLE_MULTIPLIER` | Extra weight for title matches (default 2) |
| `LABEL_WEIGHT` | Points per matching label (default 4) |
| `LABEL_USER_BONUS` | Points for a user-type label (default 6) |
| `EXPLICIT_USER_BONUS` | Points for a stated intended user (default 10) |
| `MIN_SCORE` | Minimum score to avoid defaulting to Other (default 3) |
| `RUBRIC_PROMPT` | The rubric text sent to the model in Claude mode |

To change where a task falls (for example, to treat "sysadmin" as Other), move or edit the relevant pattern in `RULES`, `LABEL_RULES`, or `USER_RULES`.

---

## Error handling and rate limits

- Items that cannot be fetched (deleted, private without a suitable token, discussions without `GITHUB_TOKEN`, network errors) are written with an empty title and the classification `Unclassified (could not fetch item)`. The script continues and reports the error on stderr.
- Cells that don't contain a recognizable GitHub issue, PR, or discussion link get the same treatment.
- Duplicate links in the input are fetched and classified once.
- When GitHub's rate limit is exhausted, the script waits until the limit resets and retries. Server errors (5xx) are retried with backoff.

---

## Limitations

- **Only the item's title, labels, and body are read.** Comment threads are not included, so an item whose purpose becomes clear only in discussion may be misclassified.
- **Keyword mode is heuristic.** It can misjudge items that use unusual phrasing or mix several topics. Review borderline results, or use `--use-claude`.
- **English-language rules.** The patterns assume English text.
- **Label rules are generic.** Check `LABEL_RULES` against your repository's actual labels.
- **Single label per item.** An item that spans several categories is assigned to the best-scoring one.
