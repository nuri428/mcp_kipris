import logging
import typing as t

import pandas as pd
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.api.korean import PatentPublicationNumberSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentPublicationNumberSearchArgs(BaseModel):
    publication_number: str = Field(..., description="Publication number, it must be filled")
    patent: bool = Field(True, description="Include patent search")
    utility: bool = Field(True, description="Include utility model search")
    lastvalue: str = Field("", description="Last value for pagination")
    docs_start: int = Field(0, description="Start index of documents")
    docs_count: int = Field(10, description="Number of documents to return")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")


class PatentPublicationNumberSearchTool(ToolHandler):
    name: str = "korean_patent_publication_number_search"
    description: str = "patent search by publication number, this tool is for korean patent search"
    api: PatentPublicationNumberSearchAPI = PatentPublicationNumberSearchAPI()
    args_schema: t.Type[BaseModel] = PatentPublicationNumberSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentPublicationNumberSearchArgs(**args)
            logger.info(f"publication_number: {validated_args.publication_number}")

            result = self.api.search(
                publication_number=validated_args.publication_number,
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
            raise ValueError("Invalid input: 공개번호(publication_number) 정보가 필요합니다.")
