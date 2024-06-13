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

# Read the current version from the VERSION file
if [ -f VERSION ]; then
  CURRENT_VERSION=$(cat VERSION)
else
  CURRENT_VERSION="0.0.0"
fi

if [ -z "$1" ]; then
  # No version number supplied, increment the current version
  VERSION=$(increment_version $CURRENT_VERSION)
else
  # Use the provided version number
  VERSION=$1
fi

# Update the VERSION file
echo $VERSION > VERSION

# Add changes and commit
git add .
git commit -m "Release version $VERSION"

# Tag the new version
git tag "v$VERSION"
git push origin main --tags

# Push the VERSION file update
git push origin main

echo "Released version $VERSION"
