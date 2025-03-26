import logging
import os
import sys
from collections.abc import Sequence
from typing import List

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.tools import (
    ForeignPatentApplicantSearchTool,
    ForeignPatentApplicationNumberSearchTool,
    ForeignPatentFreeSearchTool,
    ForeignPatentInternationalApplicationNumberSearchTool,
    ForeignPatentInternationalOpenNumberSearchTool,
    KoreanPatentApplicantSearchTool,
    KoreanPatentApplicationNumberSearchTool,
    KoreanPatentDetailSearchTool,
    KoreanPatentKeywordSearchTool,
    KoreanPatentRighterSearchTool,
    KoreanPatentSearchTool,
    KoreanPatentSummarySearchTool,
)

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")

app = Server("mcp-kipris")

tool_handlers = {}


def add_tool_handler(tool_class: ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class
    logger.info(f"Tool handler added: {tool_class.name}")


def get_tool_handler(name: str) -> ToolHandler | None:
    logger.info(f"Tool handler find: {name}")
    if name not in tool_handlers:
        return None
    logger.info(f"Tool handler found: {name}")
    return tool_handlers[name]


add_tool_handler(KoreanPatentApplicantSearchTool())
add_tool_handler(KoreanPatentKeywordSearchTool())
# add_tool_handler(KoreanPatentSearchTool)
# add_tool_handler(KoreanPatentRighterSearchTool)
# add_tool_handler(KoreanPatentApplicationNumberSearchTool)
# add_tool_handler(KoreanPatentSummarySearchTool)
# add_tool_handler(KoreanPatentDetailSearchTool)
# add_tool_handler(ForeignPatentApplicantSearchTool)
# add_tool_handler(ForeignPatentApplicationNumberSearchTool)
# add_tool_handler(ForeignPatentFreeSearchTool)
# add_tool_handler(ForeignPatentInternationalApplicationNumberSearchTool)
# add_tool_handler(ForeignPatentInternationalOpenNumberSearchTool)


@app.list_tools()
async def list_tools() -> list[Tool]:
    logger.info(f"Tool handler list: {tool_handlers.values()}")
    return [tool.get_tool_description() for tool in tool_handlers.values()]


@app.call_tool()
async def call_tool(tool_name: str, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for command line run."""
    if not isinstance(args, dict):
        raise RuntimeError("arguments must be dictionary")

    tool_handler = get_tool_handler(tool_name)
    if not tool_handler:
        raise ValueError(f"Unknown tool: {tool_name}")

    try:
        return tool_handler.run_tool(args)
    except Exception as e:
        logger.error(str(e))
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")


async def main():
    logger.info("Starting MCP KIPRIS server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio_server initialized")
            init_options = app.create_initialization_options()
            logger.info(f"Initialization options created: {init_options}")
            await app.run(read_stream, write_stream, init_options)
            # app.run(read_stream, write_stream, init_options)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
