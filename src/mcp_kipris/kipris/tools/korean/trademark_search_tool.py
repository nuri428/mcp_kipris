import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence
from typing import List

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.trademark_search_api import TrademarkSearchAPI

logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class TrademarkSearchArgs(BaseModel):
    word: str = Field(..., description="상표 검색 키워드")
    docs_start: int = Field(1, description="검색 시작 위치 (기본값: 1)")
    docs_count: int = Field(10, description="검색 결과 수 (기본값: 10, 범위: 1-30)")
    desc_sort: bool = Field(True, description="내림차순 정렬 여부 (기본값: true)")
    sort_spec: str = Field("AD", description="정렬 기준 필드 (PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자)")


class TrademarkSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("trademark_search")
        self.api = TrademarkSearchAPI(api_key=api_key)
        self.description = "trademark search by keyword, this tool is for korean trademark search"
        self.args_schema = TrademarkSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {"type": "string", "description": "상표 검색 키워드"},
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
                "required": ["word"],
            },
            metadata={
                "usage_hint": "키워드로 한국 상표를 검색하고 상표에 대한 정보를 제공합니다.",
                "example_user_queries": ["'삼성' 관련 상표를 검색해줘"],
                "preferred_response_style": (
                    "상표명, 출원일자, 상표 상태, 출원인을 포함하여 최근 순으로 표 형태로 정리해주세요. "
                    "간결하고 이해하기 쉽게 응답해 주세요."
                ),
            },
        )

    def run_tool(self, args: dict) -> List[TextContent]:
        try:
            validated_args = TrademarkSearchArgs(**args)
            logger.info(f"Searching for trademark: {validated_args.word}")

            response = self.api.sync_search(
                word=validated_args.word,
                docs_count=validated_args.docs_count,
                docs_start=validated_args.docs_start,
                sort_spec=validated_args.sort_spec,
                desc_sort=validated_args.desc_sort,
            )

            if response.empty:
                return [TextContent(type="text", text="there is no result")]

            # 상표 검색 결과의 컬럼이 특허와 다를 수 있으므로, 일반적인 컬럼만 선택
            available_columns = response.columns.tolist()
            summary_columns = []
            
            # 일반적인 상표 정보 컬럼들
            for col in ["ApplicationNumber", "ApplicationDate", "TrademarkName", "Applicant"]:
                if col in available_columns:
                    summary_columns.append(col)
            
            # 만약 위 컬럼들이 없다면, 처음 4개 컬럼을 선택
            if not summary_columns:
                summary_columns = available_columns[:4]
            
            summary_df = response[summary_columns].copy()
            return [TextContent(type="text", text=summary_df.to_markdown(index=False))]

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {str(e)}")]
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {str(e)}")]

    async def run_tool_async(self, args: dict) -> List[TextContent]:
        try:
            validated_args = TrademarkSearchArgs(**args)
            logger.info(f"Searching for trademark: {validated_args.word}")

            response = await self.api.async_search(
                word=validated_args.word,
                docs_count=validated_args.docs_count,
                docs_start=validated_args.docs_start,
                sort_spec=validated_args.sort_spec,
                desc_sort=validated_args.desc_sort,
            )

            if response.empty:
                return [TextContent(type="text", text="there is no result")]

            # 상표 검색 결과의 컬럼이 특허와 다를 수 있으므로, 일반적인 컬럼만 선택
            available_columns = response.columns.tolist()
            summary_columns = []
            
            # 일반적인 상표 정보 컬럼들
            for col in ["ApplicationNumber", "ApplicationDate", "TrademarkName", "Applicant"]:
                if col in available_columns:
                    summary_columns.append(col)
            
            # 만약 위 컬럼들이 없다면, 처음 4개 컬럼을 선택
            if not summary_columns:
                summary_columns = available_columns[:4]
            
            summary_df = response[summary_columns].copy()
            return [TextContent(type="text", text=summary_df.to_markdown(index=False))]

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {str(e)}")]
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {str(e)}")]