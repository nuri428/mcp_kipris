import logging
import typing as t

import pandas as pd
from kipris.api.korean.applicant_search_api import PatentApplicantSearchAPI
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class PatentApplicantSearchArgs(BaseModel):
    applicant: str = Field(..., description="Applicant name is required")
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


class PatentApplicantSearchTool(ToolHandler):
    name: str = "patent_applicant_search"
    description: str = "patent search by applicant name, this tool is for korean patent search"
    api: PatentApplicantSearchAPI = PatentApplicantSearchAPI()
    args_schema: t.Type[BaseModel] = PatentApplicantSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentApplicantSearchArgs(**args)
            logger.info(f"applicant: {validated_args.applicant}")

            result = self.api.search(
                applicant=validated_args.applicant,
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
            raise ValueError("Invalid input: 출원인(applicant) 정보가 필요합니다.")
