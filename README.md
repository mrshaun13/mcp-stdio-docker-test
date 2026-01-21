# MCP STDIO Docker Test Server

Minimal MCP server for testing Docker stdio communications between AI agents and MCP clients. Returns random structured JSON data without any external dependencies.

## Quick Start

Get up and running in 3 steps:

### Step 1: Build the Docker Image

```bash
./scripts/build.sh
```

This builds the `mcp-stdio-docker-test:latest` Docker image.

### Step 2: Add MCP Server Configuration

Add this configuration to your IDE's MCP settings file:

**For Claude Desktop**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows)

**For Cursor/Windsurf**: Add to your MCP configuration file

```json
{
  "mcpServers": {
    "mcp-stdio-test": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "mcp-stdio-docker-test:latest"
      ]
    }
  }
}
```

### Step 3: Test with Your AI Agent

Restart your IDE and ask your AI agent to use the MCP server:

> "Can you use the get-random-data tool from the mcp-stdio-test server?"

You should see structured JSON data returned with server metrics, process info, and random technical data.

## Available Tools

| Tool | Description |
|------|-------------|
| `get-random-data` | Returns random structured technical data (~10-15 fields) |
| `echo` | Echoes back a provided message |
| `server-status` | Returns server version and status |

## Example Output

The `get-random-data` tool returns structured data like:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-20T20:47:00+00:00",
  "server_info": {
    "hostname": "server-abc123",
    "ip_address": "192.168.1.100",
    "mac_address": "a1:b2:c3:d4:e5:f6",
    "uptime_seconds": 86400
  },
  "metrics": {
    "cpu_usage_percent": 45.5,
    "memory_used_mb": 8192,
    "memory_total_mb": 32768,
    "disk_io_read_mbps": 125.3,
    "disk_io_write_mbps": 50.2,
    "network_rx_mbps": 100.5,
    "network_tx_mbps": 25.8
  },
  "process_info": {
    "pid": 12345,
    "threads": 16,
    "open_files": 256,
    "connections": 42
  },
  "status": "healthy",
  "tags": ["prod", "web", "api"],
  "version": "2.5.10"
}
```

---

## Alternative Setup Methods

### Local Python Development

If you prefer to run without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
PYTHONPATH=src python -m mcp_stdio_test
```

**MCP Configuration for Local Python:**
```json
{
  "mcpServers": {
    "mcp-stdio-test": {
      "command": "python",
      "args": [
        "-m", "mcp_stdio_test"
      ],
      "cwd": "/path/to/mcp-stdio-docker-test",
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### Manual Docker Run

To run the container directly (without MCP client):

```bash
docker run -i mcp-stdio-docker-test:latest
```

---

## System Requirements

### Docker Deployment (Recommended)
- **Docker**: 20.10+ or compatible container runtime (Podman, containerd)
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Architecture**: x86_64 (amd64) or ARM64

### Local Python Deployment
- **Python**: 3.11 or higher
- **pip**: Latest version recommended
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 128MB RAM
- **Disk Space**: ~50MB for dependencies

### MCP Client Requirements
- Any MCP-compatible client (Claude Desktop, Cursor, Windsurf, etc.)
- Ability to execute Docker or Python commands
- stdio transport support

---

## Purpose

This server is designed to test the Docker pipeline communications between an MCP server and the LLM client. It has no external calls - just stdio MCP protocol testing.
