import logging
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.righter_search_api import PatentRighterSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentRighterSearchArgs(BaseModel):
    righter_name: str = Field(..., description="Righter name, it must be filled")
    docs_start: int = Field(1, description="Start index of documents")
    docs_count: int = Field(10, description="Number of documents to return")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")


class PatentRighterSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_righter_search")
        self.api = PatentRighterSearchAPI()
        self.description = "patent search by righter name, this tool is for korean patent search"
        self.args_schema = PatentRighterSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "righter_name": {"type": "string", "description": "권리자명"},
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10, 범위: 1-30)"},
                    "desc_sort": {"type": "boolean", "description": "내림차순 정렬 여부 (기본값: true)"},
                    "sort_spec": {
                        "type": "string",
                        "description": "정렬 기준 필드 (PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자)",
                        "enum": ["PD", "AD", "GD", "OPD"],
                        "default": "AD",
                    },
                },
                "required": ["righter_name"],
            },
            output_schema={
                "type": "object",
                "description": "pandas DataFrame 형태의 검색 결과",
                "properties": {
                    "출원번호": {"type": "string"},
                    "출원일자": {"type": "string", "format": "date"},
                    "발명의명칭": {"type": "string"},
                    "출원인": {"type": "string"},
                    "최근상태": {"type": "string"},
                    "등록번호": {"type": "string"},
                    "등록일자": {"type": "string", "format": "date"},
                    "공개번호": {"type": "string"},
                    "공개일자": {"type": "string", "format": "date"},
                    "공고번호": {"type": "string"},
                    "공고일자": {"type": "string", "format": "date"},
                },
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        try:
            validated_args = PatentRighterSearchArgs(**args)
            logger.info(f"righter_name: {validated_args.righter_name}")

            response = self.api.search(
                righter_name=validated_args.righter_name,
                docs_start=validated_args.docs_start,
                docs_count=validated_args.docs_count,
                desc_sort=validated_args.desc_sort,
                sort_spec=validated_args.sort_spec,
            )
            result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 권리자명(righter_name) 정보가 필요합니다.")
