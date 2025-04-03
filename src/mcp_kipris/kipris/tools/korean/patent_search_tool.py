import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_search_api import PatentSearchAPI

logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class PatentSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")


class PatentSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_search")
        self.api = PatentSearchAPI(api_key=api_key)
        self.description = "patent search by application number, this tool is for korean patent search"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {"application_number": {"type": "string", "description": "출원번호"}},
                "required": ["application_number"],
            },
            metadata={
                "usage_hint": "출원번호로 한국 특허를 검색하고 특허에 대한 기본적인 정보를 제공합니다.",
                "example_user_queries": ["1020230045678 특허의 기본 정보를 알고 싶어."],
                "preferred_response_style": (
                    "출원번호, 출원일자, 발명의 명칭, 출원인을 포함하여 최근 순으로 표 형태로 정리해주세요. "
                    "간결하고 이해하기 쉽게 응답해 주세요."
                ),
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        validated_args = PatentSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        response = self.api.search(application_number=validated_args.application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        summary_df = response[["ApplicationNumber", "ApplicationDate", "InventionName", "RegistrationStatus"]].copy()
        return [TextContent(type="text", text=summary_df.to_markdown(index=False))]

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """특허 검색 비동기 실행 메서드"""
        validated_args = PatentSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        # 기존 API 클래스를 asyncio.to_thread로 비동기적으로 호출
        response = await asyncio.to_thread(self.api.search, application_number=validated_args.application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        summary_df = response[["ApplicationNumber", "ApplicationDate", "InventionName", "RegistrationStatus"]].copy()
        return [TextContent(type="text", text=summary_df.to_markdown(index=False))]
