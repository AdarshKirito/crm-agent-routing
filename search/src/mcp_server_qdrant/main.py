import argparse
import os


def main():
    """
    Main entry point for the mcp-server-qdrant script defined
    in pyproject.toml. It runs the MCP server with a specific transport
    protocol.
    """

    # Parse the command-line arguments to determine the transport protocol.
    parser = argparse.ArgumentParser(description="mcp-server-qdrant")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
    )
    args = parser.parse_args()

    # Import is done here to make sure environment variables are loaded
    # only after we make the changes.
    from mcp_server_qdrant.server import mcp

    # fastmcp 3 no longer reads FASTMCP_SERVER_HOST/PORT/LOG_LEVEL, which every
    # launcher here sets, so pass them on to the HTTP transports ourselves.
    options = {}
    if args.transport != "stdio":
        for key, name, cast in (
            ("host", "FASTMCP_SERVER_HOST", str),
            ("port", "FASTMCP_SERVER_PORT", int),
            ("log_level", "FASTMCP_SERVER_LOG_LEVEL", str),
        ):
            if os.getenv(name):
                options[key] = cast(os.environ[name])
    mcp.run(transport=args.transport, **options)
