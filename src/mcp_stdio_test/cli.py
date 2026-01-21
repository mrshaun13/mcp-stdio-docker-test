"""
Command-line interface for MCP STDIO Test Server.
"""

import asyncio
import sys

from mcp_stdio_test import __version__
from mcp_stdio_test.logging_config import configure_logging, get_logger
from mcp_stdio_test.server import run_mcp_server

logger = get_logger(__name__)


def main() -> None:
    """Main CLI entry point."""
    configure_logging()
    
    logger.info(
        "Starting MCP STDIO Test Server",
        extra={"version": __version__},
    )

    try:
        asyncio.run(run_mcp_server())
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.exception("Fatal error in MCP server", extra={"error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
