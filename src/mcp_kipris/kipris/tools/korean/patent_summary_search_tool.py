import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_summary_search_api import PatentSummarySearchAPI

logger = logging.getLogger("mcp-kipris")
api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class PatentSummarySearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")


class PatentSummarySearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_summary_search")
        self.api = PatentSummarySearchAPI(api_key=api_key)
        self.description = "patent summary search by application number, this tool is for korean patent search"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {"application_number": {"type": "string", "description": "출원번호"}},
                "required": ["application_number"],
            },
            outputSchema={
                "type": "object",
                "description": "특허 요약 정보 (pandas DataFrame 형식)",
                "properties": {
                    "출원번호": {"type": "string", "description": "Patent application number"},
                    "출원일자": {"type": "string", "description": "Application date"},
                    "발명의명칭": {"type": "string", "description": "Title of the invention"},
                    "출원인": {"type": "string", "description": "Applicant name"},
                    "요약": {"type": "string", "description": "Summary of the patent"},
                    "대표도면": {"type": "string", "description": "URL of the representative drawing"},
                    "법적상태": {"type": "string", "description": "Legal status of the patent"},
                },
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        validated_args = PatentSummarySearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        response = self.api.search(application_number=validated_args.application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
        return result

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """특허 요약 검색 비동기 실행 메서드"""
        validated_args = PatentSummarySearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        # 기존 API 클래스를 asyncio.to_thread로 비동기적으로 호출
        response = await asyncio.to_thread(self.api.search, application_number=validated_args.application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
        return result
