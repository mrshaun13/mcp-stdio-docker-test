"""
MCP STDIO Docker Test Server - Minimal MCP server for testing Docker pipeline communications.
"""

from pathlib import Path

_version_file = Path(__file__).parent.parent.parent / "VERSION"
__version__ = _version_file.read_text().strip() if _version_file.exists() else "unknown"

__all__ = ["__version__"]
