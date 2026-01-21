#!/usr/bin/env python3
"""
MCP Server Log Viewer - Compact table-style log viewer for MCP server.

Usage:
    ./scripts/view-logs.py [container_name_or_id]
    
If no container name is provided, it will find the mcp-stdio-docker-test container automatically.

Features:
- Entire request/response cycle on one line
- Table-style layout with column headers
- Headers repeat every 20 lines for easy reference
- Color-coded status indicators
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Optional

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    GRAY = "\033[90m"


def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except:
        return ts[:8]

class RequestTracker:
    def __init__(self):
        self.current_request = {}
    
    def process_log(self, log: dict) -> Optional[str]:
        message = log.get("message", "")
        timestamp = format_timestamp(log.get("asctime", ""))
        
        if "MCP tool called" in message:
            self.current_request = {
                'timestamp': timestamp,
                'tool': log.get("tool_name", "?"),
                'args': log.get("arguments", {}),
            }
            return None
        
        if "MCP tool completed" in message:
            if not self.current_request:
                return None
            
            tool = self.current_request.get('tool', '?')
            args = self.current_request.get('args', {})
            duration = log.get("duration_ms", 0)
            size = log.get("response_length", 0)
            ts = self.current_request.get('timestamp', timestamp)
            
            # Format args compactly
            args_str = " ".join(f"{k}={v}" for k, v in args.items()) if args else ""
            
            result = f"{Colors.GRAY}{ts}{Colors.RESET} {Colors.GREEN}✓{Colors.RESET} {Colors.BOLD}{tool:20s}{Colors.RESET} {Colors.CYAN}{args_str:25s}{Colors.RESET} {Colors.YELLOW}{duration:>6.2f}ms{Colors.RESET} {Colors.DIM}{size:>4d}b{Colors.RESET}"
            self.current_request = {}
            return result
        
        if "MCP tool failed" in message:
            tool = self.current_request.get('tool', log.get("tool_name", "?"))
            error = log.get("error", "")[:50]
            ts = self.current_request.get('timestamp', timestamp)
            result = f"{Colors.GRAY}{ts}{Colors.RESET} {Colors.RED}✗{Colors.RESET} {Colors.BOLD}{tool:20s}{Colors.RESET} {Colors.RED}{error}{Colors.RESET}"
            self.current_request = {}
            return result
        
        if "Server Starting" in message or "MCP server starting" in message:
            version = log.get("version", "?")
            return f"\n{Colors.GREEN}{'═' * 80}\n🚀 MCP Server v{version}\n{'═' * 80}{Colors.RESET}\n"
        
        if "MCP server stopped" in message:
            return f"{Colors.YELLOW}⏹  Stopped{Colors.RESET}"
        
        return None

def print_header(container: str):
    """Print the header."""
    print(f"\n{Colors.DIM}{'─' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}MCP Server Log Viewer{Colors.RESET} - Container: {Colors.CYAN}{container}{Colors.RESET}")
    print(f"{Colors.DIM}Time     St Tool                 Arguments                  Duration Size{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 80}{Colors.RESET}")


def main():
    container = sys.argv[1] if len(sys.argv) > 1 else None
    if not container:
        # Try to find by image name first
        result = subprocess.run(
            ["docker", "ps", "--filter", "ancestor=mcp-stdio-docker-test", "--format", "{{.Names}}"],
            capture_output=True, text=True
        )
        containers = [c for c in result.stdout.strip().split("\n") if c]
        if containers:
            container = containers[0]
    
    if not container:
        print(f"{Colors.RED}No container found. Usage: {sys.argv[0]} [container_name]{Colors.RESET}")
        sys.exit(1)
    
    # Print initial header
    print_header(container)
    
    line_count = 0
    tracker = RequestTracker()
    try:
        process = subprocess.Popen(["docker", "logs", "-f", container], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            line = line.strip()
            if not line or line.startswith('{"jsonrpc":'):
                continue
            try:
                log = json.loads(line)
                formatted = tracker.process_log(log)
                if formatted:
                    print(formatted, flush=True)
                    line_count += 1
                    
                    # Reprint header every 20 lines so it's always visible
                    if line_count % 20 == 0:
                        print_header(container)
            except json.JSONDecodeError:
                pass
    except KeyboardInterrupt:
        print(f"\n{Colors.GRAY}Stopped{Colors.RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
