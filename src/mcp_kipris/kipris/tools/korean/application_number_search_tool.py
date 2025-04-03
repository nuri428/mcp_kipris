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
from mcp_kipris.kipris.api.korean.application_number_search_api import PatentApplicationNumberSearchAPI

logger = logging.getLogger("mcp-kipris")
api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class PatentApplicationNumberSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")
    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10")
    desc_sort: bool = Field(
        True,
        description="Sort in descending order; default is True, when True, sort by descending order.it mean latest date first.",
    )
    sort_spec: str = Field(
        "AD",
        description="Field to sort by; default is 'AD'(PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자, FD-국제출원일자, FOD-국제공개일자, RD-우선권주장일자)",
    )


class PatentApplicationNumberSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_application_number_search")
        self.api = PatentApplicationNumberSearchAPI(api_key=api_key)
        self.description = "Patent search by application number, this tool is for korean patent search"

    def get_tool_description(self) -> Tool:
        import sys

        logger.info(f"get_tool_description: {self.name}")
        tool = Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "application_number": {"type": "string", "description": "출원번호"},
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10)"},
                    "desc_sort": {"type": "boolean", "description": "내림차순 정렬 여부 (기본값: true)"},
                    "sort_spec": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": ["PD", "AD", "GD", "OPD", "FD", "FOD", "RD"],
                        "default": "AD",
                    },
                },
                "required": ["application_number"],
            },
        )
        logger.info(f"get_tool_description: {tool}")
        return tool

    def run_tool(self, args: dict) -> Sequence[TextContent]:
        try:
            validated_args = PatentApplicationNumberSearchArgs(**args)
            validated_args.application_number = validated_args.application_number.replace("-", "")
            logger.info(f"Searching for application number: {validated_args.application_number}")

            response = self.api.sync_search(
                application_number=validated_args.application_number,
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

            return [TextContent(type="text", text=response.to_markdown(index=False))]

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {str(e)}")]
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {str(e)}")]

    async def run_tool_async(self, args: dict) -> Sequence[TextContent]:
        try:
            validated_args = PatentApplicationNumberSearchArgs(**args)
            validated_args.application_number = validated_args.application_number.replace("-", "")
            logger.info(f"Searching for application number: {validated_args.application_number}")

            response = await self.api.async_search(
                application_number=validated_args.application_number,
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

            summary_df = response[["ApplicationNumber", "ApplicationDate", "InventionName", "Applicant"]].copy()
            return [TextContent(type="text", text=summary_df.to_markdown(index=False))]
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {str(e)}")]
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {str(e)}")]
