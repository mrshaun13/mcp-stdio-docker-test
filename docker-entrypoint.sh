#!/bin/bash
set -e

MODE="${1:-mcp}"

case "$MODE" in
    mcp)
        echo "Starting MCP STDIO Test Server..." >&2
        exec python3 -m mcp_stdio_test
        ;;
    *)
        echo "Unknown mode: $MODE" >&2
        echo "Usage: $0 {mcp}" >&2
        exit 1
        ;;
esac
