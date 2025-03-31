import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_detail_search_api import PatentDetailSearchAPI

logger = logging.getLogger("mcp-kipris")
api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class PatentDetailSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")


class PatentDetailSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_detail_search")
        self.api = PatentDetailSearchAPI(api_key=api_key)
        self.description = "patent search by applicant name"

    def get_tool_description(self) -> Tool:
        import sys

        logger.info(f"get_tool_description: {self.name}")
        tool = Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {"application_number": {"type": "string", "description": "출원번호"}},
                "required": ["application_number"],
            },
        )
        logger.info(f"get_tool_description: {tool}")
        return tool

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        validated_args = PatentDetailSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        response = self.api.search(application_number=validated_args.application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
        return result

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """특허 상세 검색 비동기 실행 메서드"""
        validated_args = PatentDetailSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        # 기존 API 클래스를 asyncio.to_thread로 비동기적으로 호출
        response = await asyncio.to_thread(self.api.search, application_number=validated_args.application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
        return result
