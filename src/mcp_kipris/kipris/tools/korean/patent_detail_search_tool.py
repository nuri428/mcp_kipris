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
    application_number: str = Field(..., description="출원번호 (숫자만, 하이픈(-) 없이 입력하세요. 예: 1020230045678)")


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
            metadata={
                "usage_hint": ("출원번호가 주어졌을 때, 해당 특허의 상세한 법적/기술적 정보를 보여줍니다."),
                "example_user_queries": [
                    "출원번호 1020250037551 특허의 상세 정보 알려줘",
                    "두 번째 특허의 구체적인 내용을 알고 싶어",
                ],
                "preferred_response_style": (
                    "정보가 많기 때문에 Markdown 형식으로 구분된 섹션별로 정리해서 보여주세요. "
                    "예: 기본정보 / 출원인정보 / 발명자정보 / 대리인정보 / 우선권정보 등"
                ),
            },
        )
        logger.info(f"get_tool_description: {tool}")
        return tool

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        validated_args = PatentDetailSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        application_number = validated_args.application_number.replace("-", "")
        response = self.api.sync_search(application_number=application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_markdown(index=False))]
        return result

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """특허 상세 검색 비동기 실행 메서드"""
        validated_args = PatentDetailSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        application_number = validated_args.application_number.replace("-", "")
        response = await self.api.async_search(application_number=application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_markdown(index=False))]
        return result
