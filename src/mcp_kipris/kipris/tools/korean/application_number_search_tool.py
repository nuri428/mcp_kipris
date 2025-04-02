import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.application_number_search_api import PatentApplicationNumberSearchAPI

logger = logging.getLogger("mcp-kipris")
api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class PatentApplicationNumberSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")
    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10")
    desc_sort: bool = Field(
        True,
        description="Sort in descending order; default is True, when True, sort by descending order.it mean latest date first.",
    )
    sort_spec: str = Field(
        "AD",
        description="Field to sort by; default is 'AD'(PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자, FD-국제출원일자, FOD-국제공개일자, RD-우선권주장일자)",
    )


class PatentApplicationNumberSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_application_number_search")
        self.api = PatentApplicationNumberSearchAPI(api_key=api_key)
        self.description = "Patent search by application number, this tool is for korean patent search"

    def get_tool_description(self) -> Tool:
        import sys

        logger.info(f"get_tool_description: {self.name}")
        tool = Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "application_number": {"type": "string", "description": "출원번호"},
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10)"},
                    "desc_sort": {"type": "boolean", "description": "내림차순 정렬 여부 (기본값: true)"},
                    "sort_spec": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": ["PD", "AD", "GD", "OPD", "FD", "FOD", "RD"],
                        "default": "AD",
                    },
                },
                "required": ["application_number"],
            },
        )
        logger.info(f"get_tool_description: {tool}")
        return tool

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        validated_args = PatentApplicationNumberSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        response = self.api.sync_search(
            application_number=validated_args.application_number,
            docs_start=validated_args.docs_start,
            docs_count=validated_args.docs_count,
            desc_sort=validated_args.desc_sort,
            sort_spec=validated_args.sort_spec,
        )

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
        return result

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """출원번호 검색 비동기 실행 메서드"""
        validated_args = PatentApplicationNumberSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        # 기존 API 클래스를 asyncio.to_thread로 비동기적으로 호출
        response = await asyncio.to_thread(
            self.api.sync_search,
            application_number=validated_args.application_number,
            docs_start=validated_args.docs_start,
            docs_count=validated_args.docs_count,
            desc_sort=validated_args.desc_sort,
            sort_spec=validated_args.sort_spec,
        )

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
        return result
