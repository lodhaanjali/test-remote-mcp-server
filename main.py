from fastmcp import FastMCP
import random
import json

# Create the FastMCP server
mcp = FastMCP("Simple Calculator Server")


# Tool 1: Add two numbers
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


# Tool 2: Generate a random number
@mcp.tool()
def random_number(min_val: int = 1, max_val: int = 100) -> int:
    """Generate a random number within a range."""
    return random.randint(min_val, max_val)


# Resource: Server information
@mcp.resource("info://server")
def server_info() -> str:
    """Get information about this MCP server."""

    info = {
        "name": "Simple Calculator Server",
        "version": "1.0.0",
        "description": "A basic MCP server with math tools",
        "tools": ["add", "random_number"],
        "author": "Your Name"
    }

    return json.dumps(info, indent=2)


# Start the server
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )