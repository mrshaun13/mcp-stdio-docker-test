# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Production-ready documentation (CHANGELOG.md, AI_README.md, SECURITY.md)
- Comprehensive security guidelines and audit

### Changed

### Fixed

### Removed

---

## [0.1.1] - 2025-01-20

### Fixed
- Enhanced logging for JSON-RPC response debugging
- Added comprehensive diagnostic logging for Windsurf stdio communications

### Changed
- Improved logging output format for better debugging

---

## [0.1.0] - 2025-01-20

### Added
- Initial release of MCP STDIO Docker Test Server
- Three core tools for testing MCP stdio communications:
  - `get-random-data`: Returns random structured technical data (~10-15 fields)
  - `echo`: Echoes back provided messages for basic communication testing
  - `server-status`: Returns server version and status information
- Docker support with hardened Alpine Linux base image
- Structured JSON logging with python-json-logger
- Comprehensive error handling and logging
- Support for both Docker and local Python execution
- MCP protocol implementation using mcp>=1.25.0
- Data validation with Pydantic
- Configurable log levels via environment variables
- Random data generation for testing:
  - Server information (hostname, IP, MAC address, uptime)
  - System metrics (CPU, memory, disk I/O, network)
  - Process information (PID, threads, open files, connections)
  - Status indicators and version tags
- Multi-record generation support (1-10 records per request)
- Optional simulated API latency for realistic testing
- Zero external dependencies (no APIs, databases, or authentication)

### Security
- No hardcoded secrets or credentials
- No sensitive data logging
- Secure Docker image based on hardened Alpine Linux
- Minimal attack surface with no external network calls

---

<!-- 
Version Format: MAJOR.MINOR.PATCH

MAJOR - Breaking changes that require user action
MINOR - New features, backward compatible
PATCH - Bug fixes, backward compatible

Categories:
- Added: New features
- Changed: Changes to existing functionality
- Deprecated: Soon-to-be removed features
- Removed: Removed features
- Fixed: Bug fixes
- Security: Security-related changes
-->
