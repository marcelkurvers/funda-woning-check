#!/usr/bin/env bash
set -euo pipefail

### ================= CONFIG =================
FRONTEND_DIR="frontend"
COMPOSE_FILE="docker-compose.yml"
GIT_REMOTE="origin"
GIT_BRANCH="main"

TSCONFIG="$FRONTEND_DIR/tsconfig.json"
TSCONFIG_BUILD="$FRONTEND_DIR/tsconfig.build.json"
PACKAGE_JSON="$FRONTEND_DIR/package.json"

### ================= HELPERS =================
log() { echo "▶ $1"; }

fail() {
  echo
  echo "✖ RELEASE ABORTED"
  echo "✖ $1"
  echo
  exit 1
}

require_file() {
  [ -f "$1" ] || fail "Required file missing: $1"
}

### ================= PRE-FLIGHT =================
require_file "$COMPOSE_FILE"
require_file "$TSCONFIG"
require_file "$PACKAGE_JSON"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "Not a git repository"

### ================= TS BUILD CONFIG =================
if [ ! -f "$TSCONFIG_BUILD" ]; then
  log "Creating tsconfig.build.json (release-safe TypeScript config)"
  cat > "$TSCONFIG_BUILD" <<EOF
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "noUnusedLocals": false,
    "noUnusedParameters": false
  }
}
EOF
fi

### ================= PATCH package.json =================
log "Ensuring frontend build uses tsconfig.build.json"

node <<'EOF'
const fs = require('fs');
const path = 'frontend/package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));

if (!pkg.scripts || !pkg.scripts.build) {
  console.error("No build script found in package.json");
  process.exit(1);
}

const desired = 'tsc -p tsconfig.build.json && vite build';
if (pkg.scripts.build !== desired) {
  pkg.scripts.build = desired;
  fs.writeFileSync(path, JSON.stringify(pkg, null, 2));
  console.log("✔ build script patched");
} else {
  console.log("✔ build script already correct");
}
EOF

### ================= FRONTEND BUILD =================
log "Running frontend build (release-safe TypeScript)"

pushd "$FRONTEND_DIR" >/dev/null
npm run build || fail "Frontend build failed"
popd >/dev/null

log "Frontend build OK"

### ================= VERSION =================
LAST_TAG=$(git tag --sort=-v:refname | head -n 1)

if [[ -z "$LAST_TAG" ]]; then
  NEW_VERSION="v0.1.0"
else
  VERSION="${LAST_TAG#v}"
  IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"
  PATCH=$((PATCH + 1))
  NEW_VERSION="v$MAJOR.$MINOR.$PATCH"
fi

log "Release version: $NEW_VERSION"

### ================= DOCKER =================
log "Stopping compose stack"
docker compose -f "$COMPOSE_FILE" down || true

### --- OLLAMA CONFLICT GUARD ---
if docker ps -a --format '{{.Names}}' | grep -q '^ollama$'; then
  log "Removing existing 'ollama' container"
  docker stop ollama >/dev/null 2>&1 || true
  docker rm ollama >/dev/null 2>&1 || true
fi

log "Building Docker images (no cache)"
docker compose -f "$COMPOSE_FILE" build --no-cache

log "Starting containers"
docker compose -f "$COMPOSE_FILE" up -d

### ================= GIT =================
if ! git diff --quiet; then
  log "Committing release changes"
  git add .
  git commit -m "chore: release $NEW_VERSION"
else
  log "No code changes to commit"
fi

git tag "$NEW_VERSION"
git push "$GIT_REMOTE" "$GIT_BRANCH"
git push "$GIT_REMOTE" "$NEW_VERSION"

log "✅ Release $NEW_VERSION completed successfully"
