import asyncio
import logging
import os
import typing as t
from collections.abc import Sequence
from typing import List

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
            metadata={
                "usage_hint": "출원번호로 한국 특허를 검색하고 요약 정보를 제공합니다.",
                "example_user_queries": ["1020230045678 특허의 요약 정보를 알고 싶어."],
                "preferred_response_style": (
                    "출원번호, 출원일자, 발명의 명칭, 출원인을 포함하여 최근 순으로 표 형태로 정리해주세요. "
                    "간결하고 이해하기 쉽게 응답해 주세요."
                ),
            },
        )

    def run_tool(self, args: dict) -> List[TextContent]:
        try:
            validated_args = PatentSummarySearchArgs(**args)
            validated_args.application_number = validated_args.application_number.replace("-", "")
            logger.info(f"Searching for application number: {validated_args.application_number}")

            response = self.api.sync_search(
                application_number=validated_args.application_number,
            )

            if response.empty:
                return [TextContent(type="text", text="there is no result")]

            return [TextContent(type="text", text=response.to_markdown(index=False))]

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {str(e)}")]
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {str(e)}")]

    async def run_tool_async(self, args: dict) -> List[TextContent]:
        try:
            validated_args = PatentSummarySearchArgs(**args)
            validated_args.application_number = validated_args.application_number.replace("-", "")
            logger.info(f"Searching for application number: {validated_args.application_number}")

            response = await self.api.async_search(
                application_number=validated_args.application_number,
            )

            if response.empty:
                return [TextContent(type="text", text="there is no result")]

            return [TextContent(type="text", text=response.to_markdown(index=False))]

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {str(e)}")]
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {str(e)}")]
