#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

VERSION=$(cat VERSION)
IMAGE_NAME="mcp-stdio-docker-test"

echo "Building ${IMAGE_NAME}:${VERSION}..."

docker build \
    --build-arg VERSION="${VERSION}" \
    -t "${IMAGE_NAME}:${VERSION}" \
    -t "${IMAGE_NAME}:latest" \
    .

echo "Build complete: ${IMAGE_NAME}:${VERSION}"
