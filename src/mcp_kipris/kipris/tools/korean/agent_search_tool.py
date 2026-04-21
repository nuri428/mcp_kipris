import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence
from typing import List

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.agent_search_api import AgentSearchAPI

logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class AgentSearchArgs(BaseModel):
    agent: str = Field(..., description="대리인명")
    patent: bool = Field(True, description="특허 포함 여부 (기본값: true)")
    utility: bool = Field(True, description="실용신안 포함 여부 (기본값: true)")
    lastvalue: str = Field("", description="특허 등록 상태 (A:공개, C:정정공개, F:공고, G:정정공고, I:무효공고, J:취소공고, R:재공고, 공백:전체)")
    docs_start: int = Field(1, description="검색 시작 위치 (기본값: 1)")
    docs_count: int = Field(10, description="검색 결과 수 (기본값: 10, 범위: 1-30)")
    desc_sort: bool = Field(True, description="내림차순 정렬 여부 (기본값: true)")
    sort_spec: str = Field("AD", description="정렬 기준 필드 (PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자)")


class AgentSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("agent_search")
        self.api = AgentSearchAPI(api_key=api_key)
        self.description = "patent search by agent name, this tool is for korean patent search"
        self.args_schema = AgentSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {"type": "string", "description": "대리인명"},
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
                "required": ["agent"],
            },
            metadata={
                "usage_hint": "대리인명으로 한국 특허를 검색하고 특허에 대한 정보를 제공합니다.",
                "example_user_queries": ["'김과장' 대리인이 처리한 특허를 검색해줘"],
                "preferred_response_style": (
                    "대리인명, 출원일자, 발명의 명칭, 출원인을 포함하여 최근 순으로 표 형태로 정리해주세요. "
                    "간결하고 이해하기 쉽게 응답해 주세요."
                ),
            },
        )

    def run_tool(self, args: dict) -> List[TextContent]:
        try:
            validated_args = AgentSearchArgs(**args)
            logger.info(f"Searching for agent: {validated_args.agent}")

            response = self.api.sync_search(
                agent=validated_args.agent,
                docs_count=validated_args.docs_count,
                docs_start=validated_args.docs_start,
                lastvalue=validated_args.lastvalue,
                patent=validated_args.patent,
                utility=validated_args.utility,
                sort_spec=validated_args.sort_spec,
                desc_sort=validated_args.desc_sort,
            )

            if response.empty:
                return [TextContent(type="text", text="there is no result")]

            summary_df = response[["applicationNumber", "applicationDate", "inventionTitle", "applicantName"]].copy()
            return [TextContent(type="text", text=summary_df.to_markdown(index=False))]

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {str(e)}")]
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {str(e)}")]

    async def run_tool_async(self, args: dict) -> List[TextContent]:
        try:
            validated_args = AgentSearchArgs(**args)
            logger.info(f"Searching for agent: {validated_args.agent}")

            response = await self.api.async_search(
                agent=validated_args.agent,
                docs_count=validated_args.docs_count,
                docs_start=validated_args.docs_start,
                lastvalue=validated_args.lastvalue,
                patent=validated_args.patent,
                utility=validated_args.utility,
                sort_spec=validated_args.sort_spec,
                desc_sort=validated_args.desc_sort,
            )

            if response.empty:
                return [TextContent(type="text", text="there is no result")]

            summary_df = response[["applicationNumber", "applicationDate", "inventionTitle", "applicantName"]].copy()
            return [TextContent(type="text", text=summary_df.to_markdown(index=False))]

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {str(e)}")]
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {str(e)}")]