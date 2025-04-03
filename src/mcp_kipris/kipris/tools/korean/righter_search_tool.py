import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.righter_search_api import PatentRighterSearchAPI

logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class PatentRighterSearchArgs(BaseModel):
    righter_name: str = Field(..., description="Righter name, it must be filled")
    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")


class PatentRighterSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_righter_search")
        self.api = PatentRighterSearchAPI(api_key=api_key)
        self.description = "patent search by righter name, this tool is for korean patent search"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "righter_name": {"type": "string", "description": "권리자 이름"},
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10)"},
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
            metadata={
                "usage_hint": "권리자 이름으로 한국 특허를 검색하고 요약 정보를 제공합니다.",
                "example_user_queries": ["삼성전자가 권리자인 특허 보여줘", "LG화학이 권리자인 특허 5건 알려줘"],
                "preferred_response_style": (
                    "권리자, 출원일자, 발명의 명칭, 출원번호를 포함하여 최근 순으로 표 형태로 정리해주세요. "
                    "간결하고 이해하기 쉽게 응답해 주세요."
                ),
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        validated_args = PatentRighterSearchArgs(**args)
        logger.info(f"righter_name: {validated_args.righter_name}")

        response = self.api.sync_search(
            rightHoler=validated_args.righter_name,
            docs_start=validated_args.docs_start,
            docs_count=validated_args.docs_count,
            desc_sort=validated_args.desc_sort,
            sort_spec=validated_args.sort_spec,
        )

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        summary_df = response[["ApplicationNumber", "ApplicationDate", "InventionName", "RegistrationStatus"]].copy()
        return [TextContent(type="text", text=summary_df.to_markdown(index=False))]

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """권리자 검색 비동기 실행 메서드"""
        validated_args = PatentRighterSearchArgs(**args)
        logger.info(f"righter_name: {validated_args.righter_name}")

        # 기존 API 클래스를 asyncio.to_thread로 비동기적으로 호출
        response = await self.api.async_search(
            rightHoler=validated_args.righter_name,
            docs_start=validated_args.docs_start,
            docs_count=validated_args.docs_count,
            desc_sort=validated_args.desc_sort,
            sort_spec=validated_args.sort_spec,
        )

        # 검색 결과가 없는 경우 처리
        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        summary_df = response[["ApplicationNumber", "ApplicationDate", "InventionName", "RegistrationStatus"]].copy()
        return [TextContent(type="text", text=summary_df.to_markdown(index=False))]
