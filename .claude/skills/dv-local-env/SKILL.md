---
name: dv-local-env
description: Start, stop, check, reset or clear the local dockerized Dataverse + React SPA development environment from /Users/jptosca/REP/IQSS/dataverse-frontend/dev-env (nginx on localhost:8000, Dataverse backend, Postgres, Solr, LocalStack S3, Keycloak, Vite dev server). Use whenever a task needs the local Dataverse running or freshly reset — e.g. "start dataverse", "spin up the dev env", "is the local instance up?", "stop the containers", "wipe/clear/reset the environment", "switch to a PR image tag", "load sample data", or before verifying behavior at localhost:8000 / localhost:8000/modern.
---

# Local Dataverse dev environment

This skill wraps the containerized environment documented in
`/Users/jptosca/REP/IQSS/dataverse-frontend/DEVELOPER_GUIDE.md` ("Running the Project
Locally → dataverse-frontend repo"). All actions go through one script:

```bash
S=/Users/jptosca/REP/jp-tosca/dv-modern-fc/.claude/skills/dv-local-env/scripts/dv-env.sh
$S status
```

When the environment is up:

| What | URL |
|---|---|
| Modern SPA (Vite, hot reload from the repo's `src/`) | http://localhost:8000/modern |
| Legacy JSF app | http://localhost:8000 |
| API | http://localhost:8000/api (also :8080 directly) |
| MailDev inbox | http://localhost:1080 |
| Solr admin | http://localhost:8983 |

Login: `dataverseAdmin` / `admin1`.

## Pick the right action

The upstream `run-env.sh` **always runs `rm-env.sh` first**, which deletes all
data. The script separates that behavior so that "start" never destroys data by
accident:

| Intent | Command | Data |
|---|---|---|
| See what's running | `$S status` | — |
| Start or resume | `$S start [tag]` | kept (created on first run) |
| Pause, free CPU/RAM | `$S stop` | kept, containers kept |
| Remove containers | `$S down` | kept in `dev-env/docker-dev-volumes` |
| Fresh instance | `$S reset [tag]` (default `unstable`) | **wiped**, then started |
| Tear down completely | `$S clear` | **wiped**, left stopped |
| Wait until usable | `$S wait [seconds]` | — |
| Add sample collections/datasets | `$S seed` | adds |
| Follow logs | `$S logs [container]` | — |

Rules:

- Always run `$S status` first. The user may already have an environment
  running, possibly with data they care about.
- `reset` and `clear` destroy the database, Solr index, and uploaded files.
  Run them only if the user asked for a fresh, clean, or wiped environment.
  When the request is ambiguous (e.g. "restart it"), use `stop` then `start`.
- To change the image tag, run `reset <tag>`. `start` refuses to change the tag
  over existing data, because a different Dataverse version on an old database
  is not a supported upgrade path here.
- PR images are on GHCR (`ghcr.io/gdcc/dataverse:<tag>`). Set
  `REGISTRY=ghcr.io` in `dev-env/.env` before `reset <tag>`, and set it back to
  `docker.io` afterwards. Tags: https://github.com/orgs/gdcc/packages/container/package/dataverse

## Starting: expect a long wait

After `start` or `reset`, run `$S wait` (use a long Bash timeout of ~600000 ms,
or run it in the background). A cold start takes several minutes. Payara must
deploy, the configbaker bootstrap must create `dataverseAdmin`, and on the
first run the frontend image installs npm dependencies. `wait` returns only
when the API answers, `/modern/` returns 200, and the bootstrap has finished.
Report the elapsed time it prints.

`seed` needs a ready instance, Python 3 and network access (it clones
`IQSS/dataverse-sample-data`). Upstream warns that its scripts sometimes fail
partway, so after seeding, check what was actually created instead of assuming
success.

## Known quirks (not failures)

- `dev_smtp` shows `unhealthy`. Its healthcheck hits `[::1]:1080`, but mail
  still works. Ignore it.
- `dev_dataverse_bootstrap`, `dv_initializer`, `dev_solr_initializer`, and
  `dev_keycloak_initializer` show `Exited (0)`. These are one-shot jobs, so
  that is expected. A non-zero exit is a real problem: check `$S logs <name>`.
  The bootstrap skips itself on an instance that is already set up, so
  `start` can be rerun safely.
- File uploads go to LocalStack at `s3.localhost:4566` on a 128 MB in-memory
  bucket. Files disappear when the container is recreated, but the database
  rows stay. If downloads break after a `down`/`start`, run `reset`. If uploads
  fail with a DNS error, the user needs `127.0.0.1 s3.localhost` in
  `/etc/hosts` (that needs sudo, so ask them).
- Port 8000, 8080, 8983, 1080, or 4566 may already be in use, for example by a
  backend started from the `IQSS/dataverse` repo. Both setups can't run at
  once. Report the conflict; don't kill the other process.

## Troubleshooting

- Docker not running → the script says so; ask the user to start Docker Desktop.
- Missing `.npmrc` in the repo root → the frontend image can't install
  `@iqss/dataverse-client-javascript`. It needs a GitHub token with
  `read:packages` (DEVELOPER_GUIDE "Prerequisites"). Ask the user; never
  create a token yourself.
- API never comes up → `$S logs dev_dataverse` (Payara deploy errors) and
  `$S logs dev_postgres`.
- SPA returns 502 → `$S logs dev_frontend`. This usually means npm dependencies
  changed; `start` uses `--build`, so rerunning it rebuilds the image.

`DV_FRONTEND_DIR` overrides the repo path if the checkout moves.
