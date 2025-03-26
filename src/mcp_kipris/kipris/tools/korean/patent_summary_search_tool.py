import logging
import typing as t

import pandas as pd
from kipris.api.korean.patent_summary_search_api import PatentSummarySearchAPI
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class PatentSummarySearchArgs(BaseModel):
    application_number: str = Field("", description="Application number")


class PatentSummarySearchTool(ToolHandler):
    name: str = "korean_patent_summary_search"
    description: str = "patent summary search. you provide application number then it will return patent summary"
    api: PatentSummarySearchAPI = PatentSummarySearchAPI()
    args_schema: t.Type[BaseModel] = PatentSummarySearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentSummarySearchArgs(**args)
            logger.info(f"application_number: {validated_args.application_number}")

            result = self.api.search(application_number=validated_args.application_number)
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 출원번호(application_number) 정보가 필요합니다.")
