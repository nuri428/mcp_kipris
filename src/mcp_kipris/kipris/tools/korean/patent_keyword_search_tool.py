import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.free_search_api import PatentFreeSearchAPI

logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class PatentKeywordSearchArgs(BaseModel):
    search_word: str = Field(..., description="Search word, it must be filled")
    patent: bool = Field(True, description="Include patent search")
    utility: bool = Field(True, description="Include utility model search")
    lastvalue: str = Field("", description="Last value for pagination")
    docs_start: int = Field(1, description="Start index of documents")
    docs_count: int = Field(10, description="Number of documents to return")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")


class PatentKeywordSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_keyword_search")
        self.api = PatentFreeSearchAPI(api_key=api_key)
        self.description = "patent search by keyword, this tool is for korean patent search"
        self.args_schema = PatentKeywordSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "search_word": {"type": "string", "description": "검색어"},
                    "patent": {"type": "boolean", "description": "특허 포함 여부 (기본값: true)"},
                    "utility": {"type": "boolean", "description": "실용신안 포함 여부 (기본값: true)"},
                    "lastvalue": {
                        "type": "string",
                        "description": "특허 등록 상태 (A:공개, C:정정공개, F:공고, G:정정공고, I:무효공고, J:취소공고, R:재공고, 공백:전체)",
                        "enum": ["A", "C", "F", "G", "I", "J", "R", ""],
                    },
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
                "required": ["search_word"],
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        try:
            validated_args = PatentKeywordSearchArgs(**args)
            logger.info(f"search_word: {validated_args.search_word}")

            response = self.api.search(
                word=validated_args.search_word,
                patent=validated_args.patent,
                utility=validated_args.utility,
                lastvalue=validated_args.lastvalue,
                docs_start=validated_args.docs_start,
                docs_count=validated_args.docs_count,
                desc_sort=validated_args.desc_sort,
                sort_spec=validated_args.sort_spec,
            )

            # 검색 결과가 없는 경우 처리
            if response.empty:
                return [TextContent(type="text", text="검색 결과가 없습니다.")]

            result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 검색어(search_word) 정보가 필요합니다.")

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """키워드 검색 비동기 실행 메서드"""
        try:
            validated_args = PatentKeywordSearchArgs(**args)
            logger.info(f"search_word: {validated_args.search_word}")

            # 기존 API 클래스를 asyncio.to_thread로 비동기적으로 호출
            response = await asyncio.to_thread(
                self.api.search,
                word=validated_args.search_word,
                patent=validated_args.patent,
                utility=validated_args.utility,
                lastvalue=validated_args.lastvalue,
                docs_start=validated_args.docs_start,
                docs_count=validated_args.docs_count,
                desc_sort=validated_args.desc_sort,
                sort_spec=validated_args.sort_spec,
            )

            # 검색 결과가 없는 경우 처리
            if response.empty:
                return [TextContent(type="text", text="검색 결과가 없습니다.")]

            result = [TextContent(type="text", text=response.to_json(orient="records", indent=2, force_ascii=False))]
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 검색어(search_word) 정보가 필요합니다.")
