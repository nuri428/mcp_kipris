import logging
import typing as t

import pandas as pd
from kipris.api.korean.righter_search_api import PatentRighterSearchAPI
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class PatentRighterSearchArgs(BaseModel):
    righter: str = Field(..., min_length=1, max_length=100, description="Righter name is required")
    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10, range is 1-30")
    patent: bool = Field(True, description="Include patents, default is True")
    utility: bool = Field(True, description="Include utility models, default is True")
    lastvalue: str = Field(
        "", description="Patent registration status; leave empty for all, (A, C, F, G, I, J, R, or empty)"
    )
    sort_spec: str = Field(
        "AD",
        description="Field to sort by; default is 'AD'(PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자, FD-국제출원일자, FOD-국제공개일자, RD-우선권주장일자)",
    )
    desc_sort: bool = Field(
        True,
        description="Sort in descending order; default is True, when True, sort by descending order.it mean latest date first.",
    )


class PatentRighterSearchTool(ToolHandler):
    name: str = "korean_patent_righter_search"
    description: str = "patent search by righter name. this tool is for korean patent search"
    api: PatentRighterSearchAPI = PatentRighterSearchAPI()
    args_schema: t.Type[BaseModel] = PatentRighterSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentRighterSearchArgs(**args)
            logger.info(f"righter: {validated_args.righter}")

            result = self.api.search(
                righter=validated_args.righter,
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
            raise ValueError("Invalid input: 권리자(righter) 정보가 필요합니다.")
