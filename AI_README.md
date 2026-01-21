# AI Development Guide - MCP STDIO Docker Test Server

> **Purpose**: Minimal MCP server for testing Docker stdio communications with zero external dependencies  
> **Repository**: https://github.com/mrshaun13/mcp-stdio-docker-test  
> **Status**: Production

---

## Project Overview

MCP STDIO Docker Test Server is a minimal Model Context Protocol (MCP) server designed specifically for testing Docker stdio pipeline communications between MCP servers and LLM clients. It provides structured random data generation without any external dependencies (no APIs, databases, or authentication), making it ideal for testing MCP protocol implementations, Docker container communications, and stdio transport reliability.

### Key Features
- **Zero External Dependencies**: No API calls, databases, or network requests - pure stdio testing
- **Docker-First Design**: Optimized for containerized deployment with hardened Alpine Linux base
- **Structured Data Generation**: Returns realistic technical metrics and system information
- **Comprehensive Logging**: JSON-formatted logs to stderr for debugging and monitoring
- **Multiple Test Tools**: Three tools covering different testing scenarios (data generation, echo, status)

---

## Tech Stack

### Language & Runtime
| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Language** | Python 3.x | Native MCP SDK support, excellent async capabilities |
| **Runtime** | Python 3 (Alpine) | Minimal footprint, fast startup, production-ready |

### Frameworks & Libraries
| Component | Choice | Purpose |
|-----------|--------|---------|
| **MCP Framework** | mcp>=1.25.0 | Official Model Context Protocol SDK |
| **Validation** | pydantic>=2.0.0 | Type validation and data modeling |
| **Logging** | python-json-logger>=3.0.0 | Structured JSON logging for production |

### Infrastructure
| Component | Details |
|-----------|---------|
| **Deployment** | Docker container (hardened Alpine Linux) |
| **Base Image** | containers.cisco.com/sto-ccc-cloud9/hardened_alpine:latest |
| **Transport** | stdio (standard input/output) |

---

## Directory Structure

```
mcp-stdio-docker-test/
├── src/
│   └── mcp_stdio_test/
│       ├── __init__.py           # Package initialization, version management
│       ├── __main__.py           # Module entry point
│       ├── cli.py                # Command-line interface
│       ├── server.py             # Core MCP server implementation
│       └── logging_config.py     # JSON logging configuration
├── scripts/
│   └── build.sh                  # Docker build script
├── Dockerfile                    # Multi-stage Docker build
├── docker-entrypoint.sh          # Container entry point
├── requirements.txt              # Python dependencies
├── VERSION                       # Version file (v0.1.1)
├── AI_README.md                  # This file
├── CHANGELOG.md                  # Version history
├── SECURITY.md                   # Security guidelines
└── README.md                     # User-facing documentation
```

---

## Architecture

### Data Flow
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ MCP Client  │────▶│    stdio     │────▶│   Server    │
│   (LLM)     │     │  Transport   │     │   Process   │
│             │◀────│ (JSON-RPC)   │◀────│             │
└─────────────┘     └──────────────┘     └─────────────┘
                                               │
                                               ▼
                                         ┌─────────────┐
                                         │   Random    │
                                         │    Data     │
                                         │ Generator   │
                                         └─────────────┘
```

### Key Components

1. **Server Module** (`src/mcp_stdio_test/server.py`)
   - Core MCP protocol implementation
   - Tool registration and handling
   - Random data generation functions
   - Async request/response processing
   - Comprehensive error handling and logging

2. **CLI Module** (`src/mcp_stdio_test/cli.py`)
   - Entry point for server execution
   - Logging configuration
   - Signal handling (SIGINT/SIGTERM)
   - Error handling and exit codes

3. **Logging Configuration** (`src/mcp_stdio_test/logging_config.py`)
   - JSON-formatted logging to stderr
   - Configurable log levels via environment variables
   - Structured logging with extra fields
   - Production-ready logging patterns

4. **Docker Entrypoint** (`docker-entrypoint.sh`)
   - Container initialization
   - Mode selection (currently only 'mcp' mode)
   - Proper signal forwarding

---

## Development Workflow

### Getting Started

```bash
# Clone repository
git clone https://github.com/mrshaun13/mcp-stdio-docker-test.git
cd mcp-stdio-docker-test

# Install dependencies (local development)
pip install -r requirements.txt

# Run development server (local)
PYTHONPATH=src python -m mcp_stdio_test

# Build Docker image
./scripts/build.sh

# Run Docker container
docker run -i mcp-stdio-docker-test:v0.1.1
```

### Common Tasks

| Task | Command |
|------|---------|
| Run server (local) | `PYTHONPATH=src python -m mcp_stdio_test` |
| Build Docker image | `./scripts/build.sh` |
| Run Docker container | `docker run -i mcp-stdio-docker-test:v0.1.1` |
| Set log level | `LOG_LEVEL=DEBUG python -m mcp_stdio_test` |
| Check version | `cat VERSION` |

---

## Code Patterns & Conventions

### Naming Conventions
- **Files**: `snake_case.py`
- **Functions**: `snake_case()`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private functions**: `_leading_underscore()`

### Error Handling Pattern
```python
try:
    # Operation that may fail
    result = await some_operation()
    logger.info("Operation succeeded", extra={"result": result})
    return result
except Exception as e:
    logger.exception("Operation failed", extra={"error": str(e)})
    return [types.TextContent(type="text", text=f"Error: {str(e)}")]
```

### Logging Pattern
```python
# Always use structured logging with extra fields
logger.info(
    "MCP tool called",
    extra={
        "tool_name": name,
        "arguments": arguments,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
)

# Log to stderr only (stdout is reserved for MCP protocol)
# Never log sensitive information
# Use appropriate log levels: DEBUG, INFO, WARNING, ERROR, EXCEPTION
```

### Async Pattern
```python
# All MCP handlers are async
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    # Use asyncio for delays/sleeps
    if include_delay:
        import asyncio
        await asyncio.sleep(delay)
    
    # Return structured responses
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

---

## MCP Tools Reference

### get-random-data
Returns random structured technical data for testing Docker stdio communications.

**Parameters:**
- `count` (integer, optional): Number of data records to generate (1-10, default: 1)
- `include_delay` (boolean, optional): Add random delay 0-500ms (default: false)

**Returns:** JSON object with server info, metrics, process info, status, tags, and version

### echo
Echoes back the provided message for basic communication testing.

**Parameters:**
- `message` (string, required): Message to echo back

**Returns:** JSON object with echoed message, timestamp, and message length

### server-status
Returns current server status and version information.

**Parameters:** None

**Returns:** JSON object with server name, version, status, timestamp, and uptime info

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PYTHONUNBUFFERED` | No | `1` | Disable Python output buffering (set in Docker) |
| `PYTHONPATH` | No | `/app/src` | Python module search path (set in Docker) |

---

## Key Files for AI Assistance

| File | Purpose | When to Modify |
|------|---------|----------------|
| `src/mcp_stdio_test/server.py` | Core MCP server logic | Adding new tools, modifying data generation |
| `src/mcp_stdio_test/cli.py` | Entry point and initialization | Changing startup behavior, signal handling |
| `src/mcp_stdio_test/logging_config.py` | Logging configuration | Adjusting log format, adding handlers |
| `Dockerfile` | Container build | Changing base image, dependencies, or build process |
| `requirements.txt` | Python dependencies | Adding/updating packages |
| `VERSION` | Version string | Bumping version for releases |
| `CHANGELOG.md` | Version history | Documenting changes for releases |

---

## Docker Build Process

The Docker build follows these steps:
1. Use hardened Alpine Linux base image
2. Install Python 3 and pip
3. Upgrade pip to patch CVE-2025-8869
4. Install Python dependencies from requirements.txt
5. Copy source code and VERSION file
6. Set up entrypoint script
7. Configure environment variables

**Build Arguments:**
- `VERSION`: Injected during build for image labeling

**Image Labels:**
- `version`: Version string from VERSION file
- `org.opencontainers.image.version`: OCI-compliant version
- `org.opencontainers.image.title`: Image title
- `org.opencontainers.image.description`: Image description

---

## Troubleshooting

### Common Issues

1. **Server not responding to MCP requests**
   - Cause: stdio transport requires interactive mode (`-i` flag)
   - Solution: Always use `docker run -i` for stdio communication

2. **Logs not appearing**
   - Cause: Logs go to stderr, not stdout
   - Solution: Check stderr output or use `docker logs` command

3. **Version showing as "unknown"**
   - Cause: VERSION file not found or not readable
   - Solution: Ensure VERSION file exists in project root and is copied to Docker image

4. **Import errors in local development**
   - Cause: PYTHONPATH not set correctly
   - Solution: Run with `PYTHONPATH=src python -m mcp_stdio_test`

5. **Container exits immediately**
   - Cause: No stdin attached or improper entrypoint
   - Solution: Use `-i` flag and verify entrypoint.sh is executable

---

## Testing Strategy

This server is designed for testing MCP protocol implementations:

1. **Basic Communication**: Use `echo` tool to verify stdio transport
2. **Data Handling**: Use `get-random-data` with count=1 for single responses
3. **Batch Processing**: Use `get-random-data` with count=10 for multiple records
4. **Latency Simulation**: Use `include_delay=true` to test async handling
5. **Status Monitoring**: Use `server-status` to verify server health

---

## Version History

See [CHANGELOG.md](./CHANGELOG.md) for detailed version history.

**Current Version:** v0.1.1

---

## Security Considerations

This server follows security best practices:
- No hardcoded secrets or credentials
- No sensitive data in logs
- Minimal attack surface (no external network calls)
- Hardened Alpine Linux base image
- Regular dependency updates
- Proper error handling without information leakage

See [SECURITY.md](./SECURITY.md) for complete security guidelines.

---

## Contributing

When contributing to this project:
1. Follow the code patterns documented above
2. Update CHANGELOG.md for user-facing changes
3. Maintain zero external dependencies
4. Add comprehensive logging for debugging
5. Test both local and Docker execution modes
6. Update this AI_README.md if architecture changes

---

## Contact & Support

- **Maintainer**: Sean Robbins
- **Repository**: https://github.com/mrshaun13/mcp-stdio-docker-test
- **Issues**: https://github.com/mrshaun13/mcp-stdio-docker-test/issues
