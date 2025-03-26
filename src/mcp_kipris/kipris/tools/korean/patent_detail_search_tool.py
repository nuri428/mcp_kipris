import logging
import typing as t

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_detail_search_api import PatentDetailSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentDetailSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number is required")


class PatentDetailSearchTool(ToolHandler):
    name: str = "patent_detail_search"
    description: str = "patent detail search by application number, this tool is for korean patent search"
    api: PatentDetailSearchAPI = PatentDetailSearchAPI()
    args_schema: t.Type[BaseModel] = PatentDetailSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {"application_number": {"type": "string", "description": "출원번호"}},
                "required": ["application_number"],
            },
            output_schema={
                "type": "object",
                "description": "pandas DataFrame 형태의 특허 상세 정보",
                "properties": {
                    "출원번호": {"type": "string"},
                    "출원일자": {"type": "string", "format": "date"},
                    "발명의명칭": {"type": "string"},
                    "출원인": {"type": "string"},
                    "발명자": {"type": "string"},
                    "IPC분류": {"type": "string"},
                    "요약": {"type": "string"},
                    "청구항": {"type": "string"},
                    "대표도면": {"type": "string", "format": "uri"},
                    "등록상태": {"type": "string"},
                    "등록번호": {"type": "string"},
                    "등록일자": {"type": "string", "format": "date"},
                },
            },
        )

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentDetailSearchArgs(**args)
            logger.info(f"application_number: {validated_args.application_number}")

            result = self.api.search(
                application_number=validated_args.application_number,
            )
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 출원번호(application_number) 정보가 필요합니다.")
