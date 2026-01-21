"""
MCP STDIO Test Server - Returns random structured JSON for pipeline testing.

This minimal MCP server is designed to test Docker stdio communications
without any external dependencies (no APIs, no databases).
"""

import json
import random
import string
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import AnyUrl

from mcp_stdio_test import __version__
from mcp_stdio_test.logging_config import get_logger

logger = get_logger(__name__)

server = Server("mcp-stdio-docker-test")


def generate_random_string(length: int = 8) -> str:
    """Generate a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_ip() -> str:
    """Generate a random IPv4 address."""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def generate_random_mac() -> str:
    """Generate a random MAC address."""
    return ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])


def generate_technical_data() -> Dict[str, Any]:
    """
    Generate random structured technical data (~10-15 fields).
    
    Returns a dictionary with various technical metrics and identifiers.
    """
    now = datetime.now(timezone.utc)
    
    return {
        "request_id": str(uuid.uuid4()),
        "timestamp": now.isoformat(),
        "server_info": {
            "hostname": f"server-{generate_random_string(6)}",
            "ip_address": generate_random_ip(),
            "mac_address": generate_random_mac(),
            "uptime_seconds": random.randint(3600, 86400 * 30),
        },
        "metrics": {
            "cpu_usage_percent": round(random.uniform(5.0, 95.0), 2),
            "memory_used_mb": random.randint(512, 16384),
            "memory_total_mb": 32768,
            "disk_io_read_mbps": round(random.uniform(0.1, 500.0), 2),
            "disk_io_write_mbps": round(random.uniform(0.1, 300.0), 2),
            "network_rx_mbps": round(random.uniform(0.01, 1000.0), 2),
            "network_tx_mbps": round(random.uniform(0.01, 500.0), 2),
        },
        "process_info": {
            "pid": random.randint(1000, 65535),
            "threads": random.randint(1, 64),
            "open_files": random.randint(10, 1000),
            "connections": random.randint(0, 500),
        },
        "status": random.choice(["healthy", "degraded", "warning", "critical"]),
        "tags": [generate_random_string(4) for _ in range(random.randint(2, 5))],
        "version": f"{random.randint(1, 5)}.{random.randint(0, 20)}.{random.randint(0, 100)}",
    }


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources (none for this test server)."""
    return []


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read resource content (not implemented)."""
    raise ValueError(f"Resource not found: {uri}")


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts (none for this test server)."""
    return []


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    """Get prompt content (not implemented)."""
    raise ValueError(f"Unknown prompt: {name}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get-random-data",
            description="Returns random structured technical data for testing Docker stdio communications. Generates ~10-15 fields of technical metrics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of data records to generate (1-10, default: 1)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 1,
                    },
                    "include_delay": {
                        "type": "boolean",
                        "description": "Add a small random delay (0-500ms) to simulate real API latency",
                        "default": False,
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="echo",
            description="Echoes back the provided message. Useful for testing basic stdio communication.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back",
                    },
                },
                "required": ["message"],
            },
        ),
        types.Tool(
            name="server-status",
            description="Returns the current server status and version information.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool call requests."""
    start_time = time.time()
    
    if arguments is None:
        arguments = {}

    logger.info("MCP tool called", extra={
        "tool_name": name,
        "arguments": arguments,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    try:
        if name == "get-random-data":
            count = min(max(arguments.get("count", 1), 1), 10)
            include_delay = arguments.get("include_delay", False)
            
            if include_delay:
                import asyncio
                delay = random.uniform(0.05, 0.5)
                await asyncio.sleep(delay)
            
            if count == 1:
                result = generate_technical_data()
            else:
                result = {"records": [generate_technical_data() for _ in range(count)], "count": count}
            
        elif name == "echo":
            message = arguments.get("message", "")
            result = {
                "echoed_message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message_length": len(message),
            }
            
        elif name == "server-status":
            result = {
                "server_name": "mcp-stdio-docker-test",
                "version": __version__,
                "status": "running",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_info": "Server is operational",
            }
            
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        duration_ms = round((time.time() - start_time) * 1000, 2)
        response_json = json.dumps(result, indent=2)
        
        # Comprehensive diagnostic logging for Windsurf stdio bug investigation
        logger.info(
            "MCP tool completed",
            extra={
                "tool_name": name,
                "duration_ms": duration_ms,
                "response_length": len(response_json),
            },
        )
        
        # Log full outbound JSON-RPC response payload for debugging
        logger.info(
            "OUTBOUND JSON-RPC RESPONSE",
            extra={
                "tool_name": name,
                "response_length": len(response_json),
                "response_payload": response_json,
                "duration_ms": duration_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "debug_outbound_message": True,
            },
        )
        
        return [types.TextContent(type="text", text=response_json)]
        
    except Exception as e:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.exception(
            "MCP tool failed",
            extra={"tool_name": name, "error": str(e), "duration_ms": duration_ms},
        )
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def run_mcp_server() -> None:
    """Run the MCP server with stdio transport."""
    logger.info("MCP server starting", extra={"version": __version__})

    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-stdio-docker-test",
                    server_version=__version__,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.exception("MCP server crashed", extra={"error": str(e)})
        raise
    finally:
        logger.info("MCP server stopped")
