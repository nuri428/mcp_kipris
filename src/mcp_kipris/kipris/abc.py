from collections.abc import Sequence

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool


class ToolHandler:
    def __init__(self, tool_name: str):
        self.name = tool_name

    def get_tool_description(self) -> Tool:
        raise NotImplementedError("Subclasses must implement this method")

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        raise NotImplementedError("Subclasses must implement this method")
