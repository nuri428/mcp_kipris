import logging
import os
from collections.abc import Sequence

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import TextContent, Tool

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
from mcp_kipris.kipris.tools.abc import ToolHandler

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")

app = Server("mcp-kipris")

tool_handlers = {}


def add_tool_handler(tool_class: ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class


def get_tool_handler(name: str) -> ToolHandler | None:
    if name not in tool_handlers:
        return None
    return tool_handlers[name]


add_tool_handler(KoreanPatentApplicantSearchTool)
add_tool_handler(KoreanPatentKeywordSearchTool)
add_tool_handler(KoreanPatentSearchTool)
add_tool_handler(KoreanPatentRighterSearchTool)
add_tool_handler(KoreanPatentApplicationNumberSearchTool)
add_tool_handler(KoreanPatentSummarySearchTool)
add_tool_handler(KoreanPatentDetailSearchTool)
add_tool_handler(ForeignPatentApplicantSearchTool)
add_tool_handler(ForeignPatentApplicationNumberSearchTool)
add_tool_handler(ForeignPatentFreeSearchTool)
add_tool_handler(ForeignPatentInternationalApplicationNumberSearchTool)
add_tool_handler(ForeignPatentInternationalOpenNumberSearchTool)


@app.list_tools()
def list_tools() -> list[Tool]:
    return [tool.get_tool_description() for tool in tool_handlers.values()]


@app.call_tool()
async def call_tool(tool_name: str, args: dict) -> Sequence[TextContent]:
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
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
