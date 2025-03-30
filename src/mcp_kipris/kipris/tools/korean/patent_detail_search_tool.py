import logging
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_detail_search_api import PatentDetailSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentDetailSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number is required")


class PatentDetailSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_detail_search")
        self.api = PatentDetailSearchAPI()
        self.description = "patent detail search by application number, this tool is for korean patent search"
        self.args_schema = PatentDetailSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {"application_number": {"type": "string", "description": "출원번호"}},
                "required": ["application_number"],
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        try:
            validated_args = PatentDetailSearchArgs(**args)
            logger.info(f"application_number: {validated_args.application_number}")

            response = self.api.search(
                application_number=validated_args.application_number,
            )
            result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 출원번호(application_number) 정보가 필요합니다.")
