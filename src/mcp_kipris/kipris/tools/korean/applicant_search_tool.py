import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.applicant_search_api import PatentApplicantSearchAPI

logger = logging.getLogger("mcp-kipris")
api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class PatentApplicantSearchArgs(BaseModel):
    applicant: str = Field(..., description="Applicant name is required")
    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10, range is 1-30")
    patent: bool = Field(True, description="Include patents, default is True")
    utility: bool = Field(True, description="Include utility models, default is True")
    lastvalue: str = Field(
        "", description="Patent registration status; leave empty for all, (A, C, F, G, I, J, R or empty)"
    )
    sort_spec: str = Field(
        "AD",
        description="Field to sort by; default is 'AD'(PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자, FD-국제출원일자, FOD-국제공개일자, RD-우선권주장일자)",
    )
    desc_sort: bool = Field(
        True,
        description="Sort in descending order; default is True, when True, sort by descending order.it mean latest date first.",
    )


class PatentApplicantSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_applicant_search")
        self.api = PatentApplicantSearchAPI(api_key=api_key)
        self.description = "patent search by applicant name, this tool is for korean patent search"

    def get_tool_description(self) -> Tool:
        import sys

        logger.info(f"get_tool_description: {self.name}")
        tool = Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "applicant": {"type": "string", "description": "출원인 이름"},
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10, 범위: 1-30)"},
                    "patent": {"type": "boolean", "description": "특허 포함 여부 (기본값: true)"},
                    "utility": {"type": "boolean", "description": "실용신안 포함 여부 (기본값: true)"},
                    "lastvalue": {
                        "type": "string",
                        "description": "특허 등록 상태 (A:공개, C:정정공개, F:공고, G:정정공고, I:무효공고, J:취소공고, R:재공고, 공백:전체)",
                        "enum": ["A", "C", "F", "G", "I", "J", "R", ""],
                    },
                    "sort_spec": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": ["PD", "AD", "GD", "OPD", "FD", "FOD", "RD"],
                        "default": "AD",
                    },
                    "desc_sort": {"type": "boolean", "description": "내림차순 정렬 여부 (기본값: true)"},
                },
                "required": ["applicant"],
            },
        )
        logger.info(f"get_tool_description: {tool}")
        return tool

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """동기 방식 실행 메서드 - 기존 호환성을 위해 유지"""
        validated_args = PatentApplicantSearchArgs(**args)
        logger.info(f"applicant: {validated_args.applicant}")

        response = self.api.search(
            applicant=validated_args.applicant,
            patent=validated_args.patent,
            utility=validated_args.utility,
            lastvalue=validated_args.lastvalue,
            docs_start=validated_args.docs_start,
            docs_count=validated_args.docs_count,
            sort_spec=validated_args.sort_spec,
            desc_sort=validated_args.desc_sort,
        )

        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        results = []
        for _, row in response.iterrows():
            results.append(TextContent(type="text", text=row.to_json(orient="records", indent=2, force_ascii=False)))

        return results

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """비동기 방식 실행 메서드"""
        validated_args = PatentApplicantSearchArgs(**args)
        logger.info(f"applicant: {validated_args.applicant}")

        # PatentApplicantSearchAPI의 search 메서드를 비동기로 호출
        # 현재 API 클래스를 그대로 사용하고 asyncio.to_thread로 비동기적으로 실행
        response = await asyncio.to_thread(
            self.api.search,
            applicant=validated_args.applicant,
            patent=validated_args.patent,
            utility=validated_args.utility,
            lastvalue=validated_args.lastvalue,
            docs_start=validated_args.docs_start,
            docs_count=validated_args.docs_count,
            sort_spec=validated_args.sort_spec,
            desc_sort=validated_args.desc_sort,
        )

        if response.empty:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]

        # 결과 처리도 비동기적으로 수행
        results = []
        for _, row in response.iterrows():
            results.append(TextContent(type="text", text=row.to_json(orient="records", indent=2, force_ascii=False)))

        return results
