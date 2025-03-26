import logging
import typing as t

import pandas as pd
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.api.korean import PatentRegistrationNumberSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentRegistrationNumberSearchArgs(BaseModel):
    registration_number: str = Field(..., description="Registration number, it must be filled")
    patent: bool = Field(True, description="Include patent search")
    utility: bool = Field(True, description="Include utility model search")
    lastvalue: str = Field("", description="Last value for pagination")
    docs_start: int = Field(0, description="Start index of documents")
    docs_count: int = Field(10, description="Number of documents to return")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")


class PatentRegistrationNumberSearchTool(ToolHandler):
    name: str = "korean_patent_registration_number_search"
    description: str = "patent search by registration number, this tool is for korean patent search"
    api: PatentRegistrationNumberSearchAPI = PatentRegistrationNumberSearchAPI()
    args_schema: t.Type[BaseModel] = PatentRegistrationNumberSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentRegistrationNumberSearchArgs(**args)
            logger.info(f"registration_number: {validated_args.registration_number}")

            result = self.api.search(
                registration_number=validated_args.registration_number,
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
            raise ValueError("Invalid input: 등록번호(registration_number) 정보가 필요합니다.")
