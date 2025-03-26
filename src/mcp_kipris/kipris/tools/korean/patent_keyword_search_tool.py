import logging
import typing as t

import pandas as pd
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.api.korean import PatentFreeSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentKeywordSearchArgs(BaseModel):
    search_word: str = Field(..., description="Search keyword, it must be filled")
    patent: bool = Field(True, description="Include patent search")
    utility: bool = Field(True, description="Include utility model search")
    lastvalue: str = Field("", description="Last value for pagination")
    docs_start: int = Field(0, description="Start index of documents")
    docs_count: int = Field(10, description="Number of documents to return")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")


class PatentKeywordSearchTool(ToolHandler):
    name: str = "korean_patent_keyword_search"
    description: str = "patent search by keyword, this tool is for korean patent search"
    api: PatentFreeSearchAPI = PatentFreeSearchAPI()
    args_schema: t.Type[BaseModel] = PatentKeywordSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentKeywordSearchArgs(**args)
            logger.info(f"search_word: {validated_args.search_word}")

            result = self.api.search(
                search_word=validated_args.search_word,
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
            raise ValueError("Invalid input: 검색어(search_word) 정보가 필요합니다.")
