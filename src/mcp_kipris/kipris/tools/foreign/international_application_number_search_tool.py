import logging
import os
import typing as t
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError, field_validator

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.foreign.international_application_number_search import (
    ForeignPatentInternationalApplicationNumberSearchAPI,
)
from mcp_kipris.kipris.tools.code import country_dict, sort_field_dict

logger = logging.getLogger("mcp-kipris")
api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


class ForeignPatentInternationalApplicationNumberSearchArgs(BaseModel):
    international_application_number: str = Field(
        ..., description="International application number, it must be filled"
    )
    current_page: int = Field(1, description="Current page number")
    sort_field: str = Field("AD", description="Sort field")
    sort_state: bool = Field(True, description="Sort state")
    collection_values: str = Field(
        "US",
        description="Collection values, must be one of: US(미국), EP(유럽), WO(PCT), JP(일본), PJ(일본영문초록), CP(중국), CN(중국특허영문초록), TW(대만영문초록), RU(러시아), CO(콜롬비아), SE(스웨덴), ES(스페인), IL(이스라엘)",
    )

    @field_validator("collection_values")
    @classmethod
    def validate_collection_values(cls, v: str) -> str:
        if v not in country_dict:
            raise ValueError(f"collection_values must be one of: {', '.join(country_dict.keys())}")
        return v

    @field_validator("sort_field")
    @classmethod
    def validate_sort_field(cls, v: str) -> str:
        if v not in sort_field_dict:
            raise ValueError(f"sort_field must be one of: {', '.join(sort_field_dict.keys())}")
        return v


class ForeignPatentInternationalApplicationNumberSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("foreign_international_application_number_search")
        self.api = ForeignPatentInternationalApplicationNumberSearchAPI(api_key=api_key)
        self.description = "foreign patent search by international application number, this tool is for foreign(US, EP, WO, JP, PJ, CP, CN, TW, RU, CO, SE, ES, IL) patent search"
        self.args_schema = ForeignPatentInternationalApplicationNumberSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "international_application_number": {"type": "string", "description": "국제출원번호"},
                    "current_page": {"type": "integer", "description": "현재 페이지 번호 (기본값: 1)"},
                    "sort_field": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": list(sort_field_dict.keys()),
                        "default": "AD",
                    },
                    "sort_state": {"type": "boolean", "description": "정렬 상태 (기본값: true)"},
                    "collection_values": {
                        "type": "string",
                        "description": "검색 대상 국가",
                        "enum": list(country_dict.keys()),
                        "default": "US",
                    },
                },
                "required": ["international_application_number"],
            },
        )

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        try:
            validated_args = ForeignPatentInternationalApplicationNumberSearchArgs(**args)
            logger.info(f"international_application_number: {validated_args.international_application_number}")

            response = await self.api.async_search(
                international_application_number=validated_args.international_application_number,
                current_page=validated_args.current_page,
                sort_field=validated_args.sort_field,
                sort_state=validated_args.sort_state,
                collection_values=validated_args.collection_values,
            )
            if response.empty:
                return [TextContent(type="text", text="검색 결과가 없습니다.")]

            summary_df = response[
                ["ApplicationNumber", "ApplicationDate", "InventionName", "RegistrationStatus"]
            ].copy()
            return [TextContent(type="text", text=summary_df.to_markdown(index=False))]
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            error_details = e.errors()
            for error in error_details:
                field = error["loc"][0]
                if field == "international_application_number":
                    raise ValueError("Invalid input: 국제출원번호(international_application_number) 정보가 필요합니다.")
                elif field == "collection_values":
                    raise ValueError(
                        f"Invalid input: 국가 코드(collection_values)는 다음 중 하나여야 합니다: {', '.join(country_dict.keys())}"
                    )
                elif field == "sort_field":
                    raise ValueError(
                        f"Invalid input: 정렬 기준(sort_field)은 다음 중 하나여야 합니다: {', '.join(sort_field_dict.keys())}"
                    )
            raise ValueError("Invalid input: 입력값이 올바르지 않습니다.")

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        try:
            validated_args = ForeignPatentInternationalApplicationNumberSearchArgs(**args)
            logger.info(f"international_application_number: {validated_args.international_application_number}")

            response = self.api.sync_search(
                international_application_number=validated_args.international_application_number,
                current_page=validated_args.current_page,
                sort_field=validated_args.sort_field,
                sort_state=validated_args.sort_state,
                collection_values=validated_args.collection_values,
            )
            if response.empty:
                return [TextContent(type="text", text="검색 결과가 없습니다.")]

            summary_df = response[
                ["ApplicationNumber", "ApplicationDate", "InventionName", "RegistrationStatus"]
            ].copy()
            return [TextContent(type="text", text=summary_df.to_markdown(index=False))]
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            error_details = e.errors()
            for error in error_details:
                field = error["loc"][0]
                if field == "international_application_number":
                    raise ValueError("Invalid input: 국제출원번호(international_application_number) 정보가 필요합니다.")
                elif field == "collection_values":
                    raise ValueError(
                        f"Invalid input: 국가 코드(collection_values)는 다음 중 하나여야 합니다: {', '.join(country_dict.keys())}"
                    )
                elif field == "sort_field":
                    raise ValueError(
                        f"Invalid input: 정렬 기준(sort_field)은 다음 중 하나여야 합니다: {', '.join(sort_field_dict.keys())}"
                    )
            raise ValueError("Invalid input: 입력값이 올바르지 않습니다.")
