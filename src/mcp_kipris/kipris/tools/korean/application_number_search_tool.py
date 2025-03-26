import logging
import typing as t

import pandas as pd
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.api.korean import PatentApplicationNumberSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentApplicationNumberSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")
    patent: bool = Field(True, description="Include patent search")
    utility: bool = Field(True, description="Include utility model search")
    lastvalue: str = Field("", description="Last value for pagination")
    docs_start: int = Field(0, description="Start index of documents")
    docs_count: int = Field(10, description="Number of documents to return")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")


class PatentApplicationNumberSearchTool(ToolHandler):
    name: str = "korean_patent_application_number_search"
    description: str = "patent search by application number, this tool is for korean patent search"
    api: PatentApplicationNumberSearchAPI = PatentApplicationNumberSearchAPI()
    args_schema: t.Type[BaseModel] = PatentApplicationNumberSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentApplicationNumberSearchArgs(**args)
            logger.info(f"application_number: {validated_args.application_number}")

            result = self.api.search(
                application_number=validated_args.application_number,
                patent=validated_args.patent,
                utility=validated_args.utility,
                lastvalue=validated_args.lastvalue,
                docs_start=validated_args.docs_start,
                docs_count=validated_args.docs_count,
                sort_spec=validated_args.sort_spec,
                desc_sort=validated_args.desc_sort,
            )
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 출원번호(application_number) 정보가 필요합니다.")
