#!/bin/bash

set -e

# Function to increment the version
increment_version() {
  local v=$1
  local delimiter=.
  local array=(${v//./ })
  array[2]=$((array[2] + 1))
  echo "${array[0]}${delimiter}${array[1]}${delimiter}${array[2]}"
}

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Read the current version from the VERSION file
if [ -f VERSION ]; then
  CURRENT_VERSION=$(cat VERSION)
  log_info "Current version: $CURRENT_VERSION"
else
  CURRENT_VERSION="0.0.0"
  log_warn "VERSION file not found. Initializing to $CURRENT_VERSION"
fi

if [ -z "$1" ]; then
  # No version number supplied, increment the current version
  VERSION=$(increment_version $CURRENT_VERSION)
  log_info "No version number supplied. Incrementing to $VERSION"
else
  # Use the provided version number
  VERSION=$1
  log_info "Using supplied version number: $VERSION"
fi

# Update the VERSION file
echo $VERSION > VERSION
log_info "Updated VERSION file to $VERSION"

# Add changes and commit
git add .
log_info "Staged all changes"
git commit -m "Release version $VERSION"
log_info "Committed changes with message: 'Release version $VERSION'"

# Tag the new version
git tag "v$VERSION"
log_info "Tagged the commit with v$VERSION"

# Push changes and tags
git push origin main --tags
log_info "Pushed changes and tags to origin/main"

# Push the VERSION file update
git push origin main
log_info "Pushed the VERSION file update"

log_info "Released version $VERSION"
