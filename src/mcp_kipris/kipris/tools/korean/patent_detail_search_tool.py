import logging
import typing as t

import pandas as pd
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.api.korean import PatentDetailSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentDetailSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")


class PatentDetailSearchTool(ToolHandler):
    name: str = "korean_patent_detail_search"
    description: str = "patent detail search. you provide application number then it will return patent detail"
    api: PatentDetailSearchAPI = PatentDetailSearchAPI()
    args_schema: t.Type[BaseModel] = PatentDetailSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentDetailSearchArgs(**args)
            logger.info(f"application_number: {validated_args.application_number}")

            result = self.api.search(application_number=validated_args.application_number)
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 출원번호(application_number) 정보가 필요합니다.")
