#!/usr/bin/env bash
# Manage the dataverse-frontend dockerized dev environment (dev-env/).
#
# Usage: dv-env.sh <command> [image-tag]
#   status            Show containers, image tag and whether the apps answer
#   start [tag]       Start/resume, KEEPING existing data (creates it if absent)
#   stop              Stop containers, keep containers and data
#   down              Remove containers, keep data (docker-dev-volumes)
#   reset [tag]       Wipe everything and start fresh (upstream run-env.sh)
#   clear             Wipe everything and leave it stopped (upstream rm-env.sh)
#   wait [seconds]    Block until the API and the SPA answer (default 900s)
#   seed              Load sample collections/datasets (upstream add-env-data.sh)
#   logs [service]    Tail logs (default dev_dataverse)
#
# Env: DV_FRONTEND_DIR overrides the repo location.

set -euo pipefail

FRONTEND_DIR="${DV_FRONTEND_DIR:-/Users/jptosca/REP/IQSS/dataverse-frontend}"
ENV_DIR="$FRONTEND_DIR/dev-env"
COMPOSE=(docker compose -f "$ENV_DIR/docker-compose-dev.yml" --project-directory "$ENV_DIR")
BASE_URL="http://localhost:8000"

die() { echo "ERROR - $*" >&2; exit 1; }
info() { echo "INFO - $*"; }

# Tag of the existing dev_dataverse container, if any.
current_tag() {
  docker inspect dev_dataverse --format '{{.Config.Image}}' 2>/dev/null | sed 's/.*://'
}

# Compose interpolates these even for stop/down/ps; set them to avoid warnings
# and a malformed image reference.
export_env() {
  export DATAVERSE_IMAGE_TAG="${1:-$(current_tag)}"
  DATAVERSE_IMAGE_TAG="${DATAVERSE_IMAGE_TAG:-unstable}"
  export COMPOSE_HTTP_TIMEOUT=200
  export DATAVERSE_BOOTSTRAP_TIMEOUT="10m"
}

preflight() {
  [ -d "$ENV_DIR" ] || die "dev-env not found at $ENV_DIR (set DV_FRONTEND_DIR)"
  docker info >/dev/null 2>&1 || die "Docker daemon is not running; start Docker Desktop"
  if [ ! -f "$ENV_DIR/.env" ]; then
    info "dev-env/.env missing; copying from .env.example"
    cp "$ENV_DIR/.env.example" "$ENV_DIR/.env"
  fi
  [ -f "$FRONTEND_DIR/.npmrc" ] || die "$FRONTEND_DIR/.npmrc missing; the frontend image build needs it (see DEVELOPER_GUIDE.md prerequisites)"
}

http_code() { curl -s -o /dev/null -w '%{http_code}' -m 5 "$1" || true; }

cmd_status() {
  local tag; tag="$(current_tag)"
  echo "Repo:       $FRONTEND_DIR"
  echo "Image tag:  ${tag:-<no dev_dataverse container>}"
  echo "Data dir:   $( [ -d "$ENV_DIR/docker-dev-volumes" ] && echo present || echo absent )"
  echo
  docker ps -a --filter 'name=^dev_|^dv_' --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null || true
  echo
  echo "API version: $(curl -s -m 5 "$BASE_URL/api/info/version" || echo 'unreachable')"
  echo "SPA  $BASE_URL/modern/ -> HTTP $(http_code "$BASE_URL/modern/")"
  echo "JSF  $BASE_URL/        -> HTTP $(http_code "$BASE_URL/")"
}

cmd_wait() {
  local timeout="${1:-900}" elapsed=0
  info "Waiting up to ${timeout}s for Dataverse API and SPA..."
  until curl -sf -m 5 "$BASE_URL/api/info/version" >/dev/null \
        && [ "$(http_code "$BASE_URL/modern/")" = "200" ]; do
    [ "$elapsed" -ge "$timeout" ] && die "not ready after ${timeout}s; check: dv-env.sh logs dev_dataverse"
    sleep 10; elapsed=$((elapsed + 10))
  done
  # Bootstrap creates dataverseAdmin; the API can answer before it finishes.
  until docker logs dev_dataverse_bootstrap 2>&1 | grep -qE 'configured for development|bootstrapped already'; do
    [ "$elapsed" -ge "$timeout" ] && die "API is up but bootstrap did not finish; check: dv-env.sh logs dev_dataverse_bootstrap"
    sleep 10; elapsed=$((elapsed + 10))
  done
  info "Ready after ~${elapsed}s: $BASE_URL/modern (SPA), $BASE_URL (JSF), login dataverseAdmin / admin1"
}

cmd_start() {
  preflight
  local existing; existing="$(current_tag)"
  if [ -n "${1:-}" ] && [ -n "$existing" ] && [ "$1" != "$existing" ]; then
    die "existing environment uses tag '$existing'; switching to '$1' needs: dv-env.sh reset $1"
  fi
  export_env "${1:-}"
  info "Starting dev env on gdcc/dataverse:$DATAVERSE_IMAGE_TAG (existing data kept)..."
  "${COMPOSE[@]}" up -d --build
}

cmd_reset() {
  preflight
  export_env "${1:-unstable}"
  info "Resetting: wiping data and starting fresh on tag $DATAVERSE_IMAGE_TAG..."
  (cd "$ENV_DIR" && ./run-env.sh "$DATAVERSE_IMAGE_TAG")
}

case "${1:-}" in
  status) cmd_status ;;
  start)  cmd_start "${2:-}" ;;
  stop)   export_env; "${COMPOSE[@]}" stop ;;
  down)   export_env; "${COMPOSE[@]}" down ;;
  reset)  cmd_reset "${2:-}" ;;
  clear)  export_env; (cd "$ENV_DIR" && ./rm-env.sh) ;;
  wait)   cmd_wait "${2:-900}" ;;
  seed)   (cd "$ENV_DIR" && ./add-env-data.sh) ;;
  logs)   docker logs --tail 100 -f "${2:-dev_dataverse}" ;;
  *) sed -n '2,15p' "$0"; exit 1 ;;
esac
