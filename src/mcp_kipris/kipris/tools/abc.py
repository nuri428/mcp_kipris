from mcp.types import Tool, TextContent
from collections.abc import Sequence
class ToolHandler():
    def __init__(self, tool_name:str):
        self.name = tool_name

    def get_tool_description(self)->Tool:
        raise NotImplementedError("Subclasses must implement this method")

    def run_tool(self, args: dict) -> Sequence[TextContent]:
        raise NotImplementedError("Subclasses must implement this method")
