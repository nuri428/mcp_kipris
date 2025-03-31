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
            outputSchema={
                "type": "object",
                "description": "특허 검색 결과 (pandas DataFrame 형식)",
                "properties": {
                    "출원번호": {"type": "string", "description": "특허 출원번호"},
                    "출원일자": {"type": "string", "description": "출원 날짜"},
                    "발명의명칭": {"type": "string", "description": "발명의 이름"},
                    "출원인": {"type": "string", "description": "출원인 이름"},
                    "요약": {"type": "string", "description": "특허 요약"},
                    "대표도면": {"type": "string", "description": "대표도면 URL"},
                    "청구항": {"type": "array", "description": "특허 청구항 목록"},
                    "발명자": {"type": "string", "description": "발명자 이름"},
                    "법적상태": {"type": "string", "description": "특허의 법적 상태"},
                    "국제출원일자": {"type": "string", "description": "국제출원일자 (있는 경우)"},
                    "국제공개일자": {"type": "string", "description": "국제공개일자 (있는 경우)"},
                    "DescriptionKR": {"type": "string", "description": "한글 설명"},
                    "DescriptionEN": {"type": "string", "description": "영어 설명"},
                },
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        validated_args = PatentSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        response = self.api.search(application_number=validated_args.application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
        return result

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """특허 검색 비동기 실행 메서드"""
        validated_args = PatentSearchArgs(**args)
        logger.info(f"application_number: {validated_args.application_number}")

        # 기존 API 클래스를 asyncio.to_thread로 비동기적으로 호출
        response = await asyncio.to_thread(self.api.search, application_number=validated_args.application_number)

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 전체 결과를 하나의 JSON으로 변환하여 반환
        result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
        return result
